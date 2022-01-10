from django.db import models

# Create your models here.
class FilesModel(models.Model):
    main = models.CharField(max_length=100,null=True)
    title = models.CharField(max_length=100,null=True)
    path=models.CharField(max_length=100,null=True)
    key_word=models.CharField(max_length=100,null=True)
    file_type=models.CharField(max_length=50,choices=[('text','text'),('video','video'),('sound','sound'),('image','image')],default=('text','text'))
    def __str__(self):
        return self.title
class userModel(models.Model):
    name=models.CharField(max_length=100,null=True)
    password=models.CharField(max_length=100,null=True)
    learning_type=models.CharField(max_length=50,choices=[('لفظي','لفظي'),('بصري','بصري'),('_','_')],default=('_','_'))
    def __str__(self):
        return self.name

