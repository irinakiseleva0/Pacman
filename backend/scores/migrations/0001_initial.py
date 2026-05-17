from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=150, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["username"]},
        ),
        migrations.CreateModel(
            name="Score",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mode", models.CharField(db_index=True, max_length=32)),
                ("value", models.PositiveIntegerField()),
                ("seed", models.IntegerField()),
                ("date", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("player", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="scores.player")),
            ],
            options={"ordering": ["-value", "date"]},
        ),
        migrations.AddIndex(
            model_name="score",
            index=models.Index(fields=["mode", "-value"], name="score_mode_value_idx"),
        ),
    ]
