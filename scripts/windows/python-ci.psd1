# Read by the hub's Invoke-PythonCiBuild.ps1; PackagingPythonVersion builds the cp314 wheels the release ships.
@{
    PackageName            = 'kataglyphis_webdavclient'
    PythonVersions         = '3.13 3.14 3.14t'
    FreeThreadedExtras     = 'tests'
    PackagingPythonVersion = '3.14'
}
