//
// Created by kooltew on 4/30/2021.
//

#ifndef KB_KNAPSACK_PARTITION_SOLUTION_PATHS_H
#define KB_KNAPSACK_PARTITION_SOLUTION_PATHS_H

#if defined(_WIN32)
#include <windows.h>
#include <Shlwapi.h>
#include <io.h>
#include <pathcch.h>

#define access _access_s
#endif

#ifdef __APPLE__
#include <libgen.h>
    #include <limits.h>
    #include <mach-o/dyld.h>
    #include <unistd.h>
#endif

#ifdef __linux__
#include <limits.h>
    #include <libgen.h>
    #include <unistd.h>

    #if defined(__sun)
        #define PROC_SELF_EXE "/proc/self/path/a.out"
    #else
        #define PROC_SELF_EXE "/proc/self/exe"
    #endif

#endif

namespace MyPaths {

#if defined(_WIN32)

    std::string getExecutablePath() {
        char rawPathName[MAX_PATH];
        GetModuleFileNameA(NULL, rawPathName, MAX_PATH);
        return std::string(rawPathName);
    }

    std::string getExecutableDir() {
        std::string executablePath = getExecutablePath();
        return executablePath.substr( 0, executablePath.find_last_of( '\\' ) +1 );
    }


#endif

#ifdef __linux__

    std::string getExecutablePath() {
   char rawPathName[PATH_MAX];
   realpath(PROC_SELF_EXE, rawPathName);
   return  std::string(rawPathName);
}

std::string getExecutableDir() {
    std::string executablePath = getExecutablePath();
    char *executablePathStr = new char[executablePath.length() + 1];
    strcpy(executablePathStr, executablePath.c_str());
    char* executableDir = dirname(executablePathStr);
    delete [] executablePathStr;
    return std::string(executableDir);
}

std::string mergePaths(std::string pathA, std::string pathB) {
  return pathA+"/"+pathB;
}

#endif

#ifdef __APPLE__
    std::string getExecutablePath() {
        char rawPathName[PATH_MAX];
        char realPathName[PATH_MAX];
        uint32_t rawPathSize = (uint32_t)sizeof(rawPathName);

        if(!_NSGetExecutablePath(rawPathName, &rawPathSize)) {
            realpath(rawPathName, realPathName);
        }
        return  std::string(realPathName);
    }

    std::string getExecutableDir() {
        std::string executablePath = getExecutablePath();
        char *executablePathStr = new char[executablePath.length() + 1];
        strcpy(executablePathStr, executablePath.c_str());
        char* executableDir = dirname(executablePathStr);
        delete [] executablePathStr;
        return std::string(executableDir);
    }

    std::string mergePaths(std::string pathA, std::string pathB) {
        return pathA+"/"+pathB;
    }
#endif


    bool checkIfFileExists (const std::string& filePath) {
        return access( filePath.c_str(), 0 ) == 0;
    }

}


#endif //KB_KNAPSACK_PARTITION_SOLUTION_PATHS_H
