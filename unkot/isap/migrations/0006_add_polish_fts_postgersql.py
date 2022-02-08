from django.db import migrations

SQL_CREATE_POLISH_CONFIG = """
/* source: https://skilldepository.com/entries/postgres-polish-dictionary */

BEGIN;
      CREATE TEXT SEARCH CONFIGURATION public.polish ( COPY = pg_catalog.english );

      CREATE TEXT SEARCH DICTIONARY polish_ispell (
        TEMPLATE = ispell,
        DictFile = polish,
        AffFile = polish,
        StopWords = polish
      );

      ALTER TEXT SEARCH CONFIGURATION polish
        ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
        WITH polish_ispell;
COMMIT;
"""

SQL_DROP_POLISH_CONFIG = """
/* source: https://skilldepository.com/entries/postgres-polish-dictionary */

BEGIN;
      DROP TEXT SEARCH CONFIGURATION IF EXISTS public.polish;
      DROP TEXT SEARCH CONFIGURATION IF EXISTS polish;
      DROP TEXT SEARCH DICTIONARY         IF EXISTS polish_ispell;
COMMIT;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("isap", "0005_alter_searchisap_last_run_ts"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_CREATE_POLISH_CONFIG, reverse_sql=SQL_DROP_POLISH_CONFIG
        )
    ]
