import httpx
import requests
from tailor.models import FileSetUpload, FileSet


class S3Client(httpx.Client):

    def upload_files(self, fileset_upload: FileSetUpload, fileset: FileSet):

        for local_files, fileset_links in zip(fileset_upload.tags.values(),
                                              fileset.tags):
            for local_file, fileset_link in zip(local_files, fileset_links.links):

                with open(local_file, 'rb') as f:
                    # fallback to requests due to missing support for put-upload in httpx
                    response = requests.put(fileset_link.url, data=f)
                    # response = self.put(fileset_link.url, data=f)
