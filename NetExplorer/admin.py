from django.contrib import admin
from NetExplorer.models import Dataset, UserDatasetPermission, ExperimentType, Experiment, UserExperimentPermission, ConditionType, Condition, ExpressionAbsolute, ExpressionRelative, SubCondition
# Register your models here.

admin.site.register(Dataset)
admin.site.register(UserDatasetPermission)
admin.site.register(ExperimentType)
admin.site.register(Experiment)
admin.site.register(UserExperimentPermission)
admin.site.register(ConditionType)
admin.site.register(Condition)
admin.site.register(ExpressionAbsolute)
admin.site.register(ExpressionRelative)
admin.site.register(SubCondition)

