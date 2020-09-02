import httpx
import requests
from tailor.models import FileSetUpload, FileSet


class FileClient(httpx.Client):

    def upload_files(self, fileset_upload: FileSetUpload, fileset: FileSet):

        for local_files, fileset_links in zip(fileset_upload.tags.values(),
                                              fileset.tags):
            for local_file, fileset_link in zip(local_files, fileset_links.links):

                with open(local_file, 'rb') as f:
                    # alt 1 not working:
                    # response = self.put(fileset_link.url, data=f)

                    # alt 2 not working:
                    # request = self.build_request('PUT', fileset_link.url, data=f)
                    # del request.headers['Transfer-Encoding']
                    # response = self.send(request)

                    # fallback to requests due to missing support for put-upload in httpx
                    response = requests.put(fileset_link.url, data=f)
