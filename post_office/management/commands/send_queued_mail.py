from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from django.db import connection as db_connection
from django.core.management.base import BaseCommand
from django.utils import timezone
from post_office.dblock import db_lock, TimeoutException, LockedException
from post_office.connections import connections
from post_office.mail import get_queued, split_emails, _send_bulk
from post_office.settings import get_batch_delivery_timeout


class Command(BaseCommand):
    processes = 1

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--processes',
            type=int,
            default=1,
            help='Number of processes used to send emails',
        )
        parser.add_argument(
            '-l', '--log-level',
            '--log-level',
            type=int,
            help='"0" to log nothing, "1" to only log errors',
        )

    def handle(self, *args, **options):
        self.processes = options['processes']
        self.send_queued_mail_until_done()

    def send_queued_mail_until_done(self):
        try:
            with db_lock('send_queued_mail_until_done'):
                self.stdout.write('Acquired lock for sending queued email')
                while True:
                    try:
                        self.send_queued()
                    except Exception as e:
                        #self.stderr.write(e)
                        raise

                    db_connection.close()

                    if not get_queued().exists():
                        break
        except TimeoutException:
            self.stderr.write('Sending queued mail requires too long, terminating now.')

        except LockedException:
            self.stderr.write('Failed to acquire lock, terminating now.')

    def send_queued(self):
        queued_emails = get_queued()
        total_sent, total_failed, total_requeued = 0, 0, 0
        total_email = len(queued_emails)

        self.stdout.write(f"Starting sending {total_email} emails with {self.processes} processes.")

        if queued_emails:

            if total_email < self.processes:
                self.processes = total_email

            if self.processes == 1:
                total_sent, total_failed, total_requeued = _send_bulk(queued_emails, uses_multiprocessing=False)

            else:
                email_lists = split_emails(queued_emails, self.processes)

                pool: Pool = Pool(processes=self.processes)

                tasks = []
                for email_list in email_lists:
                    tasks.append(pool.apply_async(_send_bulk, args=(email_list,)))

                timeout = get_batch_delivery_timeout()
                results = []

                for task in tasks:
                    results.append(task.get(timeout=timeout))

                pool.terminate()
                pool.join()

                total_sent = sum(result[0] for result in results)
                total_failed = sum(result[1] for result in results)
                total_requeued = [result[2] for result in results]

        self.stdout.write(f"{total_email} emails attempted, "
                          f"{total_sent} send, "
                          f"{total_failed} failed,"
                          f" {total_requeued} requeued.")

        return total_sent, total_failed, total_requeued
