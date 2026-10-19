# Read by the hub's Invoke-PythonCiBuild.ps1; packaging takes the pinned X.Y, so the release ships its cpXY and cpXYt wheels.
@{
    PackageName        = 'kataglyphis_webdavclient'
    PythonVersions     = 'pinned pinnedt'
    FreeThreadedExtras = 'tests'
}
