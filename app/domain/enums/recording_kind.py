from enum import Enum


class RecordingKind(str, Enum):
    ORIGIN = "origin"
    DESTINATION = "destination"
    NOTES = "notes"
