# -*- coding: utf-8 -*-
from ..item import Item


class Project(Item):
    """
    This class describes a project object child of Item class
    """

    def get_all(self, show_all=False):
        """
        Gets all projects accessible by the connected user

        :param      show_all:  Add completed and trashed projects
        :type       show_all:  boolean, optional

        :returns:   List of Project class
        :rtype:     List of :class:`~aquarium.items.project.Project`
        """
        query = list()
        query.append('# $Project')

        if not show_all:
            query.append('AND item.data.completion != 1 AND item.data.completion != -1 AND NOT (<($Trash)- *)')

        query.append('SORT item.data.name ASC')
        result = self.parent.query(meshql=' '.join(query))
        result = [self.parent.cast(data) for data in result]
        return result

    def get_shots(self):
        """
        Gets all the shots of the project

        :returns:   List of Shot class, Edge class and Tasks
        :rtype:     List of dictionary {item: :class:`~aquarium.items.shot.Shot`, edge: :class:`~aquarium.edge.Edge`, tasks: [:class:`~aquarium.items.task.Task`]}
        """
        query = "# -($Child, 5)> 0, 0 $Shot VIEW $view"
        aliases = {
            "view": {
                "item": 'item',
                "edge": 'edge',
                "tasks": '# -($Child)> $Task VIEW item'
            }
        }
        result = self.traverse(meshql=query, aliases=aliases)
        result = [self.parent.element(data) for data in result]
        return result

    def get_assets(self):
        """
        Gets all the assets of the project

        :returns:   List of Asset class, Edge class and Tasks
        :rtype:     List of dictionary {item: :class:`~aquarium.items.asset.Asset`, edge: :class:`~aquarium.edge.Edge`, tasks: [:class:`~aquarium.items.task.Task`]}
        """
        query = "# -($Child, 5)> 0, 0 $Asset VIEW $view"
        aliases = {
            "view": {
                "item": 'item',
                "edge": 'edge',
                "tasks": '# -($Child)> $Task VIEW item'
            }
        }
        result = self.traverse(meshql=query, aliases=aliases)
        result = [self.parent.element(data) for data in result]
        return result
