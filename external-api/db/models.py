from tortoise import fields
from tortoise.models import Model as TortoiseModel


class Scans(TortoiseModel):
    id = fields.IntField(pk=True)
    time_start = fields.DatetimeField()
    time_end = fields.DatetimeField(null=True)
    parts: fields.ReverseRelation["Parts"]


class Makers(TortoiseModel):
    id = fields.IntField(pk=True)
    maker = fields.CharField(max_length=255, unique=True)
    parts: fields.ReverseRelation["Parts"]


class Categories(TortoiseModel):
    id = fields.IntField(pk=True)
    category = fields.CharField(max_length=255, unique=True)
    parts: fields.ReverseRelation["Parts"]


class Models(TortoiseModel):
    id = fields.IntField(pk=True)
    model = fields.CharField(max_length=255, unique=True)
    parts: fields.ReverseRelation["Parts"]


class Parts(TortoiseModel):
    id = fields.IntField(pk=True)
    maker = fields.ForeignKeyField("models.Makers", related_name="parts")
    category = fields.ForeignKeyField("models.Categories", related_name="parts")
    model = fields.ForeignKeyField("models.Models", related_name="parts")
    part_number = fields.CharField(max_length=255)
    part_category = fields.CharField(max_length=255)
    url = fields.TextField()
    scan = fields.ForeignKeyField("models.Scans", related_name="parts")

    class Meta:
        unique_together = ("maker", "category", "model", "part_number", "part_category", "scan")
