from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

from django.db import connection as db_connection
from django.core.management.base import BaseCommand
from django.utils import timezone

from post_office.connections import connections
from post_office.lockfile import FileLock, FileLocked, default_lockfile
from post_office.mail import get_queued, split_emails
from post_office.settings import get_threads_per_process


class Command(BaseCommand):
    lockfile = default_lockfile
    processes = 1

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--processes',
            type=int,
            default=1,
            help='Number of processes used to send emails',
        )
        parser.add_argument(
            '-L', '--lockfile',
            default=default_lockfile,
            help='Absolute path of lockfile to acquire',
        )
        # parser.add_argument(
        #     '-l', '--log-level',
        #     type=int,
        #     help='"0" to log nothing, "1" to only log errors',
        # )

    def handle(self, *args, **options):
        options['verbosity']
        self.lockfile = options['lockfile']
        self.processes = options['processes']
        self.send_queued_mail_until_done()

    def send_queued_mail_until_done(self):
        """
        Send mail in queue batch by batch, until all emails have been processed.
        """
        try:
            with FileLock(self.lockfile):
                self.stdout("Acquired lock for sending queued emails at %s.lock", self.lockfile)
                while True:
                    try:
                        self.send_queued()
                    except Exception as e:
                        self.stderr(e, extra={'status_code': 500})
                        raise

                    # Close DB connection to avoid multiprocessing errors
                    db_connection.close()

                    if not get_queued().exists():
                        break
        except FileLocked:
            self.stdout("Failed to acquire lock, terminating now.")

    def send_queued(self):
        """
        Sends out all queued mails that has scheduled_time less than now or None
        """
        queued_emails = get_queued()
        total_sent, total_failed, total_requeued = 0, 0, 0
        total_email = len(queued_emails)

        self.stdout("Started sending %s emails with %s processes." %
                    (total_email, self.processes))

        if queued_emails:
            # Don't use more processes than number of emails
            if total_email < self.processes:
                processes = total_email

            if self.processes == 1:
                total_sent, total_failed, total_requeued = self.send_bulk(emails=queued_emails)
            else:
                email_lists = split_emails(queued_emails, self.processes)

                pool = Pool(self.processes)
                results = pool.map(self.send_bulk, email_lists)
                pool.terminate()

                total_sent = sum(result[0] for result in results)
                total_failed = sum(result[1] for result in results)
                total_requeued = [result[2] for result in results]

        self.stdout(
            "%s emails attempted, %s sent, %s failed, %s requeued",
            total_email, total_sent, total_failed, total_requeued,
        )

    def send_bulk(self, emails):
        if self.processes > 1:
            # Multiprocessing does not play well with database connection
            # Fix: Close connections on forking process
            # https://groups.google.com/forum/#!topic/django-users/eCAIY9DAfG0
            db_connection.close()

        sent_emails = []
        failed_emails = []  # This is a list of two tuples (email, exception)
        email_count = len(emails)

        def send(email):
            try:
                email.dispatch(log_level=log_level, commit=False,
                               disconnect_after_delivery=False)
                sent_emails.append(email)
                logger.debug('Successfully sent email #%d' % email.id)
            except Exception as e:
                logger.exception('Failed to send email #%d' % email.id)
                failed_emails.append((email, e))

        # Prepare emails before we send these to threads for sending
        # So we don't need to access the DB from within threads
        for email in emails:
            # Sometimes this can fail, for example when trying to render
            # email from a faulty Django template
            try:
                email.prepare_email_message()
            except Exception as e:
                logger.exception('Failed to prepare email #%d' % email.id)
                failed_emails.append((email, e))

        number_of_threads = min(get_threads_per_process(), email_count)
        pool = ThreadPool(number_of_threads)
        pool.map(send, emails)
        pool.close()
        pool.join()

        connections.close()

        # Update statuses of sent emails
        email_ids = [email.id for email in sent_emails]
        Email.objects.filter(id__in=email_ids).update(status=STATUS.sent)

        # Update statuses and conditionally requeue failed emails
        num_failed, num_requeued = 0, 0
        max_retries = get_max_retries()
        scheduled_time = timezone.now() + get_retry_timedelta()
        emails_failed = [email for email, _ in failed_emails]

        for email in emails_failed:
            if email.number_of_retries is None:
                email.number_of_retries = 0
            if email.number_of_retries < max_retries:
                email.number_of_retries += 1
                email.status = STATUS.requeued
                email.scheduled_time = scheduled_time
                num_requeued += 1
            else:
                email.status = STATUS.failed
                num_failed += 1

        Email.objects.bulk_update(emails_failed, ['status', 'scheduled_time', 'number_of_retries'])

        # If log level is 0, log nothing, 1 logs only sending failures
        # and 2 means log both successes and failures
        if log_level >= 1:

            logs = []
            for (email, exception) in failed_emails:
                logs.append(
                    Log(email=email, status=STATUS.failed,
                        message=str(exception),
                        exception_type=type(exception).__name__)
                )

            if logs:
                Log.objects.bulk_create(logs)

        if log_level == 2:

            logs = []
            for email in sent_emails:
                logs.append(Log(email=email, status=STATUS.sent))

            if logs:
                Log.objects.bulk_create(logs)

        logger.info(
            'Process finished, %s attempted, %s sent, %s failed, %s requeued',
            email_count, len(sent_emails), num_failed, num_requeued,
        )

        return len(sent_emails), num_failed, num_requeued
