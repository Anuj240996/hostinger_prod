from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0119_appauthlink_userapp'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS user_app (
                id BIGSERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                role TEXT,
                created_at TIMESTAMP WITH TIME ZONE,
                last_login TIMESTAMP WITH TIME ZONE
            );
            CREATE TABLE IF NOT EXISTS app_auth_links (
                id BIGSERIAL PRIMARY KEY,
                auth_user_id BIGINT NOT NULL,
                app_user_id BIGINT REFERENCES user_app(id) ON DELETE CASCADE,
                token TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS app_auth_links_auth_user_id_idx
                ON app_auth_links(auth_user_id);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
