import os, shutil, subprocess


def cleanup():
    dirs = ["build", "dist"]
    for i in dirs:
        if os.path.isdir(i):
            shutil.rmtree(i)


if __name__ == '__main__':


    #cleanup_prev
    cleanup()

    #build_hostcollector
    cmd = ["python", "-O", "-m", "PyInstaller"]
    cmd.append("main.spec")

    subprocess.run(cmd)

    #move to root
    os.replace(os.curdir+"\\dist\\kds_maintenance_widget.exe", os.curdir+"\\kds_maintenance_widget.exe")

    #cleanup
    cleanup()