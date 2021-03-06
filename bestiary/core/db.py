# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Miguel Ángel Fernández <mafesan@bitergia.com>
#

import copy
import re

import django.db.utils

from grimoirelab_toolkit.datetime import datetime_utcnow

from .errors import AlreadyExistsError, NotFoundError
from .models import (Ecosystem,
                     Project,
                     Operation)
from .utils import validate_field, validate_name


def find_ecosystem(ecosystem_id):
    """Find an ecosystem.

    Find an ecosystem by its id in the database. When the
    ecosystem does not exist the function will raise
    a `NotFoundError`.

    :param ecosystem_id: id of the ecosystem to find

    :returns: an ecosystem object

    :raises NotFoundError: when the ecosystem with the
        given `ecosystem_id` does not exist
    """

    try:
        ecosystem = Ecosystem.objects.get(id=ecosystem_id)
    except Ecosystem.DoesNotExist:
        raise NotFoundError(entity='Ecosystem ID {}'.format(ecosystem_id))
    else:
        return ecosystem


def find_project(project_id):
    """Find a project.

    Find a project by its id in the database. When the
    project does not exist the function will raise
    a `NotFoundError`.

    :param project_id: id of the project to find

    :returns: a project object

    :raises NotFoundError: when the project with the
        given `project_id` does not exist
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise NotFoundError(entity='Project ID {}'.format(project_id))
    else:
        return project


def add_ecosystem(trxl, name, title, description):
    """Add an ecosystem to the database.

    This function adds a new ecosystem to the database,
    using the given `name` as an identifier and an optional title and
    description. Name cannot be empty or `None`, the title and description
    cannot be empty.

    It returns a new `Ecosystem` object.

    :param trxl: TransactionsLog object from the method calling this one
    :param name: name of the ecosystem
    :param title: title of the ecosystem
    :param description: description of the ecosystem

    :returns: a new ecosystem

    :raises ValueError: when `name` is `None` or empty, when `title` or
        `description` is empty
    :raises AlreadyExistsError: when an instance with the same name
        already exists in the database
    """
    # Setting operation arguments before they are modified
    op_args = {
        'name': name,
        'title': title,
        'description': description
    }

    # Check if the name fulfills the requirements
    validate_name(name)
    validate_field('title', title, allow_none=True)
    validate_field('description', description, allow_none=True)

    ecosystem = Ecosystem(name=name,
                          title=title,
                          description=description)

    try:
        ecosystem.save()
    except django.db.utils.IntegrityError as exc:
        _handle_integrity_error(Ecosystem, exc)

    trxl.log_operation(op_type=Operation.OpType.ADD, entity_type='ecosystem',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=op_args['name'])

    return ecosystem


def add_project(trxl, ecosystem, name, title, parent):
    """Add an project to the database.

    This function adds a new project to the database,
    using the given `name` as an identifier and an optional title. Name cannot
    be empty or `None`, the title cannot be empty.

    It returns a new `Project` object.

    :param trxl: TransactionsLog object from the method calling this one
    :param name: name of the project
    :param title: title of the project
    :param parent: Project to be set as parent of the project to be created

    :returns: a new project

    :raises ValueError: when `name` is `None` or empty or when `title` is empty
    :raises AlreadyExistsError: when an instance with the same name
        already exists in the database
    """
    # Setting operation arguments before they are modified
    op_args = {
        'name': name,
        'title': title,
        'ecosystem': ecosystem.id,
        'parent': parent.id if parent else None
    }

    # Check if the name fulfills the requirements
    validate_name(name)
    validate_field('title', title, allow_none=True)

    if (parent) and (parent.ecosystem != ecosystem):
        raise ValueError('Parent cannot belong to a different ecosystem')

    project = Project(name=name,
                      title=title,
                      ecosystem=ecosystem,
                      parent_project=parent)

    try:
        project.save()
    except django.db.utils.IntegrityError as exc:
        _handle_integrity_error(Project, exc)

    trxl.log_operation(op_type=Operation.OpType.ADD, entity_type='project',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=op_args['name'])

    return project


def update_ecosystem(trxl, ecosystem, **kwargs):
    """Update ecosystem.

    This function allows to edit or update the information of the
    given ecosystem. The values to update are given
    as keyword arguments. The allowed keys are listed below
    (other keywords will be ignored):

       - `name`: name of the ecosystem
       - `title`: title of the ecosystem
       - `description`: description of the ecosystem

    As a result, it will return the `Ecosystem` object with
    the updated data.

    :param trxl: TransactionsLog object from the method calling this one
    :param ecosystem: ecosystem which will be updated
    :param kwargs: parameters to edit the ecosystem

    :returns: the updated ecosystem object

    :raises ValueError: raised either when the given ecosystem name is None
        or empty
    :raises TypeError: raised either when the given ecosystem name, title or
        description are not a string
    """
    def to_none_if_empty(x):
        return None if not x else x

    # Setting operation arguments before they are modified
    op_args = copy.deepcopy(kwargs)
    op_args.update({'id': ecosystem.id})

    if 'name' in kwargs:
        # Check if the name fulfills the requirements
        validate_name(kwargs['name'])
        ecosystem.name = kwargs['name']
    if 'title' in kwargs:
        title = to_none_if_empty(kwargs['title'])
        validate_field('title', title, allow_none=True)
        ecosystem.title = title
    if 'description' in kwargs:
        description = to_none_if_empty(kwargs['description'])
        validate_field('description', description, allow_none=True)
        ecosystem.description = description

    try:
        ecosystem.save()
    except django.db.utils.IntegrityError as exc:
        _handle_integrity_error(Ecosystem, exc)

    trxl.log_operation(op_type=Operation.OpType.UPDATE, entity_type='ecosystem',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=str(op_args['id']))

    return ecosystem


def update_project(trxl, project, **kwargs):
    """Update project information.

    This function allows to edit or update the information of the
    given project. The values to update are given
    as keyword arguments. The allowed keys are listed below
    (other keywords will be ignored):

       - `name`: name of the project
       - `title`: title of the project

    As a result, it will return the `Project` object with
    the updated data.

    :param trxl: TransactionsLog object from the method calling this one
    :param project: project which will be updated
    :param kwargs: parameters to edit the project

    :returns: the updated project object

    :raises ValueError: raised either when the given project name is None
        or empty
    :raises TypeError: raised either when the given project name or title are
        not a string
    """
    def to_none_if_empty(x):
        return None if not x else x

    # Setting operation arguments before they are modified
    op_args = copy.deepcopy(kwargs)
    op_args.update({'id': project.id})

    if 'name' in kwargs:
        # Check if the name fulfills the requirements
        validate_name(kwargs['name'])
        project.name = kwargs['name']
    if 'title' in kwargs:
        title = to_none_if_empty(kwargs['title'])
        validate_field('title', title, allow_none=True)
        project.title = title

    try:
        project.save()
    except django.db.utils.IntegrityError as exc:
        _handle_integrity_error(Project, exc)

    trxl.log_operation(op_type=Operation.OpType.UPDATE, entity_type='project',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=str(op_args['id']))

    return project


def delete_ecosystem(trxl, ecosystem):
    """Remove an ecosystem from the database.

    Function that removes from the database the ecosystem
    given in `ecosystem`.

    :param trxl: TransactionsLog object from the method calling this one
    :param ecosystem: ecosystem to remove
    """
    # Setting operation arguments before they are modified
    op_args = {
        'id': ecosystem.id
    }

    ecosystem.delete()

    trxl.log_operation(op_type=Operation.OpType.DELETE, entity_type='ecosystem',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=str(op_args['id']))


def delete_project(trxl, project):
    """Remove an project from the database.

    Function that removes from the database the project
    given in `project`.

    :param trxl: TransactionsLog object from the method calling this one
    :param project: project to remove
    """
    # Setting operation arguments before they are modified
    op_args = {
        'id': project.id
    }

    project.delete()

    trxl.log_operation(op_type=Operation.OpType.DELETE, entity_type='project',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=str(op_args['id']))


def link_parent_project(trxl, project, parent_project):
    """Link a project object with another with a child-parent relation.

    This method sets the `parent_project` field value from `project` with the
    `Project` object from `parent_project`. If this field already had a value,
    it will be overwritten. In case the parent project is invalid, the method
    will raise an `ValueError`.
    The reasons for considering a parent as invalid are:
      - The parent is already set to the project.
      - The parent and the project are the same.
      - The parent belongs to a different ecosystem.
      - The parent is a descendant from the project.

    :param trxl: TransactionsLog object from the method calling this one
    :param project: Source project to be linked
    :param parent_project: Parent project to be linked to the source project

    :returns: the updated project object

    :raises ValueError: raised either when the given parent project is invalid
    """
    def _is_descendant(project, from_project):
        """Check if a project is a descendant of another"""

        queue = [from_project]
        while queue:
            cur_project = queue.pop(0)
            for subproject in cur_project.subprojects.all():
                if subproject == project:
                    return True
                queue.append(subproject)

    # Setting operation arguments before they are modified
    op_args = {
        'id': project.id,
        'parent_id': parent_project.id if parent_project else None
    }

    if project.parent_project == parent_project:
        raise ValueError('Parent is already set to the project')
    if project == parent_project:
        raise ValueError('Project cannot be its own parent')
    if parent_project and (project.ecosystem != parent_project.ecosystem):
        raise ValueError('Parent cannot belong to a different ecosystem')
    if _is_descendant(parent_project, project):
        raise ValueError('Parent cannot be a descendant')

    project.parent_project = parent_project

    try:
        project.save()
    except django.db.utils.IntegrityError as exc:
        _handle_integrity_error(Project, exc)

    trxl.log_operation(op_type=Operation.OpType.LINK, entity_type='project',
                       timestamp=datetime_utcnow(), args=op_args,
                       target=str(op_args['id']))

    return project


_MYSQL_DUPLICATE_ENTRY_ERROR_REGEX = re.compile(r"Duplicate entry '(?P<value>.+)' for key")


def _handle_integrity_error(model, exc):
    """Handle integrity error exceptions."""

    m = re.match(_MYSQL_DUPLICATE_ENTRY_ERROR_REGEX,
                 exc.__cause__.args[1])
    if not m:
        raise exc

    entity = model.__name__
    eid = m.group('value')

    raise AlreadyExistsError(entity=entity, eid=eid)
