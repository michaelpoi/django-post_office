Some issues I would like to solve:

* Replace file based lock against database lock.
* Completely remove Pythons `ThreadPool`, since it does not work well with database cursors.
* Move Pythons (Process)-`Pool` into management command, since a Request-Response-Cycle never shall fork any process.
* Remove configuration option `CONTEXT_FIELD_CLASS`.
* Reformat Python code for better readability.
* Replace Django tests against PyTest.
* Use [MailHog](https://github.com/mailhog/MailHog) for testing.
* Move documentation to ReadTheDocs.