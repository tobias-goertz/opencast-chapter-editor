# UI-Config

```
{
  "upload": {
    "saveWorkflowID": "save-uploaded-assets",
    "publishWorkflowID": "publish-uploaded-segments",
    "postData": {
        "assets": {
            "options": [{
              "id": "catalog_segments_xml",
              "type": "catalog",
              "flavorType": "mpeg-7",
              "flavorSubType": "segments",
              "displayOrder": 4,
              "accept": ".xml",
              "title": "Uplaod Segments"
            }]
        },
        "processing": {
            "workflow": "",
            "configuration": {
                "uploadedSearchPreview": "true",
                "downloadSourceflavorsExist": "true",
                "download-source-flavors": "mpeg-7/segments"
            }
        }
    }
  }
}

```
