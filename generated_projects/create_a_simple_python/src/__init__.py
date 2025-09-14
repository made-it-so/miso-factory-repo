from .models import Project

def create_project(name):
    project = Project()
    project.name = name
    return project