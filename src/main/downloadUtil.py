import datetime
import urllib.error
import urllib.request
import urllib.parse
import os.path
import json
from enum import Enum
from threading import Lock

from utilImport import *

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent, }

class Repos(Enum):
    ENTITIES = "entities"
    CN = "CN"
    OPERATOR_IMAGES = "operatorImages"
    MODULE_IMAGES = "moduleTypeImages"
    MATERIAL_IMAGES = "materialImages"

REPOSITORIES = {
    Repos.ENTITIES: [CONFIG.entityListRepository, "entityLists/"],
    Repos.CN: [CONFIG.dataRepository, CONFIG.dataRepositoryGameDataPath],
    Repos.OPERATOR_IMAGES: [CONFIG.imageRepository, "avatars/"],
    Repos.MODULE_IMAGES: [CONFIG.imageRepository, "equip/type/"],
    Repos.MATERIAL_IMAGES: [CONFIG.imageRepository, "items/"]
}

DYNAMIC_DATA_PATH = "data/"

DOWNLOAD_METADATA_FILE = DYNAMIC_DATA_PATH + "downloadMetadata.json"
DOWNLOAD_METADATA = None

def writeDownloadMetadata(metadata):
    f = safeOpen(DOWNLOAD_METADATA_FILE, "w+")
    json.dump(metadata, f, indent=4)
    f.close()

if not os.path.isfile(DOWNLOAD_METADATA_FILE):
    writeDownloadMetadata({})
DOWNLOAD_METADATA = json.load(open(DOWNLOAD_METADATA_FILE, "r"))

LAST_COMMIT_TIMESTAMPS_LOCK = Lock()
LAST_COMMIT_TIMESTAMPS = {}

def checkLastCommitTime(repo, localPath):
    LAST_COMMIT_TIMESTAMPS_LOCK.acquire()
    if not repo in LAST_COMMIT_TIMESTAMPS:
        commitTimestamp = getMostRecentCommitTimestamp(repo)
        if commitTimestamp is not None:
            LAST_COMMIT_TIMESTAMPS[repo] = commitTimestamp
        else:
            LAST_COMMIT_TIMESTAMPS[repo] = DOWNLOAD_METADATA.get(localPath, 0)
    LAST_COMMIT_TIMESTAMPS_LOCK.release()


def getDownloadedFilePath(repo, filename):
    return DYNAMIC_DATA_PATH + repo.value + "/" + filename

def loadDownloadedJson(repo, filename):
    return json.load(open(getDownloadedFilePath(repo, filename), "r", encoding="utf-8"))

def tryDownloadFile(repo, filename, replaceFile = True):
    repoName, folder = REPOSITORIES[repo]
    tryDownloadFileFromGithub(repoName, folder + filename, getDownloadedFilePath(repo, filename), replaceFile)

def tryDownloadFiles(updates, progressCallback = None, replaceFile = True):
    for i, u in enumerate(updates):
        repoKey, filename = u
        if progressCallback is not None:
            progressCallback(i, len(updates))
        tryDownloadFile(repoKey, filename, replaceFile)

def buildGithubDownloadUrl(repo, remotePath):
    return f"https://raw.githubusercontent.com/{repo}/HEAD/{remotePath}"

def tryDownloadFileFromGithub(repo, remotePath, localPath, monitorChanges = True):
    global DOWNLOAD_METADATA

    checkLastCommitTime(repo, localPath)

    downloadFileFromWeb(buildGithubDownloadUrl(repo, remotePath), localPath, replace=False)

    if monitorChanges:
        if localPath in DOWNLOAD_METADATA:
            lastDownloadAttempt = DOWNLOAD_METADATA[localPath]
            if lastDownloadAttempt < LAST_COMMIT_TIMESTAMPS[repo]:
                remoteTimestamp = getMostRecentCommitTimestamp(repo, remotePath)
                if lastDownloadAttempt < remoteTimestamp:
                    downloadFileFromWeb(buildGithubDownloadUrl(repo, remotePath), localPath, replace=True)

        DOWNLOAD_METADATA[localPath] = LAST_COMMIT_TIMESTAMPS[repo]
        writeDownloadMetadata(DOWNLOAD_METADATA)

def getMostRecentCommitTimestamp(repo, remotePath=None):
    url = f"https://api.github.com/repos/{repo}/commits"
    if remotePath is not None:
        url += "?path=" + remotePath

    response = getRequest(url)
    if response is not None:
        responseJson = json.loads(response)
        return datetime.datetime.fromisoformat(responseJson[0]["commit"]["author"]["date"]).timestamp()

def downloadFileFromWeb(url, localPath, replace=False):
    if replace or not os.path.exists(localPath) and not CONFIG.offlineMode:
        LOGGER.debug("Updating from Web: %s", localPath)
        file = getRequest(url)
        if file is not None:
            f = safeOpen(localPath, mode="wb+")
            f.write(file)
            f.close()
            return True
        else:
            return False

def getRequest(url):
    try:
        if not CONFIG.offlineMode:
            return urllib.request.urlopen(urllib.request.Request(url, None, headers), timeout=CONFIG.webRequestTimeout).read()
    except urllib.error.HTTPError as response:
        LOGGER.error("Error(%s) reading url: %s", response.code, url)
        for line in response.readlines()[:10]:
            line = line.decode("utf-8")
            LOGGER.debug(line.replace("\n", ""))
    except urllib.error.URLError as error:
        LOGGER.error("Error reading %s: %s", url, error.reason)
