from django.contrib import admin

from haystack_rq_test.models import Dog, Toy


class ToyInlineAdmin(admin.StackedInline):
    model = Toy
    extra = 0
    max_num = None


class DogAdmin(admin.ModelAdmin):
    inlines = [ToyInlineAdmin, ]


admin.site.register(Dog, DogAdmin)
