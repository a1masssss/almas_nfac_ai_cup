# Generated manually for video order field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_quizattempt_quizanswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['order']},
        ),
    ] 