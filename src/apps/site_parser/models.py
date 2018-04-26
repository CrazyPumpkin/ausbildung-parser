from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Vacancy(models.Model):
    """
    Vacancy info
    """
    uuid = models.UUIDField(_("uuid"))
    is_active = models.BooleanField(_("is active"), default=True)
    title = models.CharField(_("title"), max_length=128, default="")
    starts_at = models.DateTimeField(_("starts at"), null=True)
    ends_at = models.DateTimeField(_("ends at"), null=True)
    description = models.TextField(_("description"),
                                   default="")
    image_list = ArrayField(
        models.URLField(),default=[]
    )
    location = models.ForeignKey("City", verbose_name=_('city'), null=True,
                                 on_delete=models.CASCADE)
    company = models.ForeignKey("Company", verbose_name=_('company'),
                                null=True,
                                on_delete=models.CASCADE)

    class Meta(object):
        verbose_name = _("vacancy")
        verbose_name_plural = _("vacancies")

    def __str__(self):
        return "{title} starts at {starts_at} | {company}".format(
            title=self.title, starts_at=self.starts_at, company=self.company)


class Company(models.Model):
    """
    Company info
    """
    name = models.CharField(_("name"), max_length=128, default="")
    logo = models.CharField(_("logo"), max_length=128, default="")

    class Meta(object):
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return self.name


class City(models.Model):
    """
    City info
    """
    name = models.CharField(_("location"), max_length=128, default="")

    class Meta(object):
        verbose_name = _("city")
        verbose_name_plural = _("cities")

    def __str__(self):
        return self.name
