from django.contrib import admin
from NetExplorer.models import Dataset, \
    UserDatasetPermission, \
    ExperimentType, \
    ExperimentDataset, \
    Experiment, \
    UserExperimentPermission, \
    ConditionType, \
    Condition, \
    ExpressionAbsolute, \
    ExpressionRelative, \
    Sample, \
    SampleCondition, \
    ExperimentGene, \
    RegulatoryLinks, \
    ClusterMarkers
    
# Register your models here.

admin.site.register(Dataset)
admin.site.register(UserDatasetPermission)
admin.site.register(ExperimentType)
admin.site.register(Experiment)
admin.site.register(ExperimentDataset)
admin.site.register(UserExperimentPermission)
admin.site.register(ConditionType)
admin.site.register(Condition)
admin.site.register(ExpressionAbsolute)
admin.site.register(ExpressionRelative)
admin.site.register(Sample)
admin.site.register(SampleCondition)
admin.site.register(ExperimentGene)
admin.site.register(RegulatoryLinks)
admin.site.register(ClusterMarkers)
