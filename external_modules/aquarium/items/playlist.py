# -*- coding: utf-8 -*-
from ..item import Item
import logging
logger = logging.getLogger(__name__)


class Playlist(Item):
    """
    This class describes a Playlist object child of Item class.
    """

    def get_medias(self, track=None):
        """
        Gets the medias of the playlist

        :param      track:    The ID of the track. If no track specified, all medias will be returned
        :type       track:    integer (0 or 1), optional (default: None)

        :returns:   List of Media object
        :rtype:     List of dictionary {media: :class:`~aquarium.items.media.Media`, track: integer, versionKey: integer}
        """

        filter = ''
        if track != None:
            filter = 'AND edge.data.track == {0}'.format(track)

        query = '# -($Child OR $Playlist)> 0,5000 $Media {0} UNIQUE SORT edge.createdAt ASC VIEW $view'.format(
            filter)
        aliases = {
            'view': {
                'media': 'item',
                'track': 'edge.data.track',
                'versionKey': 'edge.data.versionKey'
            }
        }

        result=self.traverse(meshql=query, aliases=aliases)
        result=[self.parent.element(data) for data in result]
        return result

    def get_playlists(self):
        """
        Gets the playlists added in this playlist

        :returns:   List of Playlist object
        :rtype:     List of :class:`~aquarium.items.playlist.Playlist`
        """

        query = '# -($Child)> $Playlist VIEW item'

        result=self.traverse(meshql=query)
        result = [self.parent.cast(item) for item in result]
        return result

    def import_medias(self, media_paths, track=0):
        """
        Import media files into the playlist

        :param      media_paths:    List of media file paths that need to be imported in the playlist
        :type       media_paths:    list, optional
        :param      track:          The ID of the track where the media will be imported. If no track specified, media are imported in the first track
        :type       track:          integer (0 or 1), optional (default: 0)

        :returns:   List of Media object
        :rtype:     List of :class:`~aquarium.items.media.Media`
        """
        medias = []
        if track > 1:
            track = 1
        elif track < 0:
            track = 0

        for file in media_paths:
            edge_data = {
                'track': track
            }
            media = self.append(type='Media', path=file, edge_data=edge_data)
            medias.append(media.item)

        return medias

    def add_playlist(self, playlist_key):
        """
        Add an existing playlist into the current playlist

        :param      playlist_key: The playlist _key to add in the current playlist
        :type       playlist_key: string

        :returns:   The created edge between the current playlist and the imported one
        :rtype:     :class:`~aquarium.edge.Edge`
        """

        return self.parent.edge.create(type='Child', from_key=self._key, to_key=str(playlist_key))

    def remove_media(self, media_key):
        """
        Remove media from the playlist

        :param      media_key:    Item media _key to remove from the playlist
        :type       media_key:    string

        :returns:   None
        :rtype:     None
        """

        query = '# -($Child OR $Playlist)> 0,1 $Media AND item._key == "{0}" VIEW edge'.format(media_key)
        media_edge = self.traverse(meshql=query)

        if len(media_edge) > 0:
            edge = self.parent.cast(media_edge[0])
            edge.delete()

    def remove_playlist(self, playlist_key):
        """
        Remove the imported playlist from the current playlist

        :param      media_key:    Item playlist _key to remove from the playlist
        :type       media_key:    string

        :returns:   None
        :rtype:     None
        """

        query = '# -($Child OR $Playlist)> 0,1 $Playlist AND item._key == "{0}" VIEW edge'.format(playlist_key)
        playlist_edge = self.traverse(meshql=query)

        if len(playlist_edge) > 0:
            edge = self.parent.cast(playlist_edge[0])
            edge.delete()

    def change_media_track(self, media_key, track=0):
        """
        Move the media to another track

        :param      media_key:    Item media _key to remove from the playlist
        :type       media_key:    string
        :param      track:        The ID of the track where the media will be imported. If no track specified, media are imported in the first track
        :type       track:        integer (0 or 1), optional (default: 0)

        :returns:   None
        :rtype:     None
        """

        query = '# -($Child OR $Playlist)> 0,1 $Media AND item._key == "{0}" VIEW edge'.format(media_key)
        media_edge = self.traverse(meshql=query)

        if len(media_edge) > 0:
            edge = self.parent.cast(media_edge[0])
            data = {
                'track': track
            }
            edge.update_data(data=data)

