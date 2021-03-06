#!/usr/bin/python
"""This script is used to discover video files, or photo files"""

import os
import logging
import exif_processing
from osc_models import VisualData, Photo, Video

LOGGER = logging.getLogger('osc_tools.visual_data_discoverer')


class VisualDataDiscoverer:
    """This class is a abstract discoverer of visual data files"""

    @classmethod
    def discover(cls, path: str) -> ([VisualData], str):
        """This method will discover visual data and will return paths and type"""
        pass

    @classmethod
    def discover_using_type(cls, path: str, osc_type: str):
        """this method is discovering the online visual data knowing the type"""
        pass


class PhotoDiscovery(VisualDataDiscoverer):
    """This class will discover all photo files"""

    @classmethod
    def discover(cls, path: str) -> ([VisualData], str):
        """This method will discover photos"""
        LOGGER.debug("searching for photos %s", path)
        if not os.path.isdir(path):
            return [], "photo"

        files = os.listdir(path)
        photos = []

        for file_path in files:
            file_name, file_extension = os.path.splitext(file_path)
            if ("jpg" in file_extension or "jpeg" in file_extension) and \
                    "thumb" not in file_name.lower():
                photo = cls._photo_from_path(os.path.join(path, file_path))
                if photo:
                    photos.append(photo)
        # Sort photo list
        cls._sort_photo_list(photos)
        # Add index to the photo objects
        index = 0
        for photo in photos:
            photo.index = index
            index += 1

        return photos, "photo"

    @classmethod
    def _photo_from_path(cls, path) -> Photo:
        photo = Photo(path)
        return photo

    @classmethod
    def _sort_photo_list(cls, photos):
        photos.sort(key=lambda p: int("".join(filter(str.isdigit, os.path.basename(p.path)))))


class ExifPhotoDiscoverer(PhotoDiscovery):
    """This class will discover all photo files having exif data"""

    @classmethod
    def _photo_from_path(cls, path) -> Photo:
        photo = Photo(path)
        tags_data = exif_processing.all_tags(photo.path)
        # required data
        photo.gps_timestamp = exif_processing.gps_timestamp(tags_data)
        photo.latitude = exif_processing.gps_latitude(tags_data)
        photo.longitude = exif_processing.gps_longitude(tags_data)
        if not photo.latitude or \
                not photo.longitude or \
                not photo.gps_timestamp:
            return None
        # optional data
        photo.exif_timestamp = exif_processing.timestamp(tags_data)
        photo.gps_speed = exif_processing.gps_speed(tags_data)
        photo.gps_altitude = exif_processing.gps_altitude(tags_data)
        photo.gps_compass = exif_processing.gps_compass(tags_data)
        return photo

    @classmethod
    def _sort_photo_list(cls, photos):
        photos.sort(key=lambda p: p.gps_timestamp)


class VideoDiscoverer(VisualDataDiscoverer):
    """This class will discover any sequence having a list of videos"""

    @classmethod
    def discover(cls, path: str) -> ([VisualData], str):
        if not os.path.isdir(path):
            return [], "video"

        files = os.listdir(path)
        videos = []

        for file_path in files:
            _, file_extension = os.path.splitext(file_path)
            if "mp4" in file_extension:
                video = Video(os.path.join(path, file_path))
                videos.append(video)
        cls._sort_list(videos)
        index = 0
        for video in videos:
            video.index = index
            index += 1

        return videos, "video"

    @classmethod
    def _sort_list(cls, videos):
        videos.sort(key=lambda v: int("".join(filter(str.isdigit, os.path.basename(v.path)))))
