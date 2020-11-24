# Instruction to create gold standard documents
## Gold standard document format
```
{
    "id": ""
    "url": ""
    "html": "..."
    "text": "Only the text of the html. Referenced as full text"
    "gold_standard_annotation": [{
        "post_text": {"surface_form": "...", "start": 200, "end": 555},
        "datetime": {"surface_form": "02-March-2012 00:58", "start": 10, "end": 29},
        "user": {"surface_form": "http://blog.angelman-asa.org/profile.php?2,1606", "start": 30, "end": 77},
        "post_link": {"surface_form": "msg-772", "start": 100, "end": 107},
    }]
}
```
## Instruction
1. First you need to download the forum pages for which you want to create a gold document. This is done by executing the script `data/serialize-test-data.py`. But first you have to add or comment out (remove # at the beginning) the url of the forum page in the file `data/test-urls.lst`.
2. Next, a first version of the gold document is created with `pre-processing.py`. Example command:
`python3  pre-processing.py ./data/forum/ --result-directory ./goldDocumentsPre/`
3. The next step is to clean up the document for the following elements:
`datetime.surface_form, user.surface_form, post_link.surface_form`
The elements that are not correctly recognized should be corrected or supplemented. For the user the link is used if available, otherwise the displayed name.
4. Now the script `python3 remove-link.py ./goldDocumentsPre/` is executed. This removes all links from the full text of the gold document except those of user and post_link.
5. Now clean up the `post_text.surface_form` elements in the gold document. These must be found in the full text and must match the correct post text.
6. Now run the script `python3 final-processing.py ./goldDocumentsPre/ --result-directory ./goldDocuments/`. If all elements are prepared correctly, a start and end position is found for each element. If this is not the case, the log will show the message "Not found in text". If start and end positions are not found, correct the pre document accordingly and generate the final document again.
7. With git commit and push to repository.

**Note**: the `final-processing.py` and `pre-processing.py` scripts do not overwrite existing documents.