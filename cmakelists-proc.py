import sqlite3
import contextlib
from pathlib import Path

from scikit_build_core.ast.ast import parse
from scikit_build_core.ast.tokenizer import tokenize


with contextlib.closing(sqlite3.connect("cmakelists_contents.db")) as cnx_backend:
    cursor = cnx_backend.cursor()
    res = cursor.execute("SELECT * FROM cmakelists")
    i = 0
    failed = []
    try:
        while line := res.fetchone():
            if i % 1000 == 0:
                print("Processed", i)
            name, version, path, contents = line
            if (
                path
                in {
                    "packages/roltrilinos/roltrilinos-0.0.9.tar.gz/roltrilinos-0.0.9/packages/seacas/libraries/ioss/src/visualization/ParaViewCatalystIossAdapter/parser/jsoncpp-master/CMakeLists.txt",
                    "packages/roltrilinos/roltrilinos-0.0.9.tar.gz/roltrilinos-0.0.9/packages/seacas/libraries/ioss/src/visualization/ParaViewCatalystIossAdapter/parser/CMakeLists.txt",
                    "packages/OpenROAD-OpenDbPy/OpenROAD-OpenDbPy-0.0.0.tar.gz/OpenROAD-OpenDbPy-0.0.0/src/codeGenerator/impl/CMakeLists.txt",
                    "packages/fprime-tools/fprime-tools-3.4.4.tar.gz/fprime-tools-3.4.4/test/fprime/fbuild/cmake-data/testbuild/CMakeLists.txt",
                    "packages/cpptools/cpptools-1.2.10-py3-none-any.whl/oasc/tmpl/CMakeLists.txt",  # template
                    "packages/cupcake/cupcake-1.1.2.tar.gz/cupcake-1.1.2/src/cupcake/data/new/tests/CMakeLists.txt",  # template
                    "packages/cupcake/cupcake-1.1.2.tar.gz/cupcake-1.1.2/src/cupcake/data/new/CMakeLists.txt",
                    "packages/scikit-build/scikit_build-0.18.0.tar.gz/scikit_build-0.18.0/tests/samples/fail-with-syntax-error-cmakelists/CMakeLists.txt",  # intentional fail (note: hangs)
                    "packages/cppiniter/cppiniter-1.1.18.tar.gz/cppiniter-1.1.18/cppiniter/files/src/CMakeLists.txt",  # template
                    "packages/cppiniter/cppiniter-1.1.18.tar.gz/cppiniter-1.1.18/cppiniter/files/CMakeLists.txt",
                    "packages/toolkit-py/toolkit-py-1.5.10.tar.gz/toolkit-py-1.5.10/toolkit/template/scaffold/project/cpp/qt5/example/console/CMakeLists.txt",  # Jinja
                    "packages/toolkit-py/toolkit-py-1.5.10.tar.gz/toolkit-py-1.5.10/toolkit/template/scaffold/project/cpp/qt5/console/CMakeLists.txt",
                    "packages/toolkit-py/toolkit-py-1.5.10.tar.gz/toolkit-py-1.5.10/toolkit/template/scaffold/project/cpp/qt5/qml/CMakeLists.txt",
                    "packages/toolkit-py/toolkit-py-1.5.10.tar.gz/toolkit-py-1.5.10/toolkit/template/scaffold/project/cpp/example/CMakeLists.txt",
                    "packages/toolkit-py/toolkit-py-1.5.10.tar.gz/toolkit-py-1.5.10/toolkit/template/scaffold/project/cpp/qt5/example/qml/CMakeLists.txt",  # template
                    "packages/LbDevTools/LbDevTools-2.0.41.tar.gz/LbDevTools-2.0.41/LbDevTools/templates/lb-dev/CMakeLists.txt",  # template
                    "packages/cpp-init/cpp_init-1.3.0.tar.gz/cpp_init-1.3.0/cpp_init/cpp-init-res/CMakeLists.txt",  # template
                    "packages/conan-recipe-generator/conan-recipe-generator-0.0.1.tar.gz/conan-recipe-generator-0.0.1/conan_recipe_generator/template/files/all/test_package/CMakeLists.txt",  # template
                    "packages/conan-recipe-generator/conan-recipe-generator-0.0.1.tar.gz/conan-recipe-generator-0.0.1/conan_recipe_generator/template/files/all/CMakeLists.txt",  # template
                    "packages/simple-ai-server/simple_ai_server-0.1.9.tar.gz/simple_ai_server-0.1.9/simple_ai/serve/cpp/CMakeLists.txt",  # extra word in file
                }
            ):
                continue
            try:
                for node in parse(tokenize(contents)):
                    pass
            except AssertionError as e:
                failed.append(f"{path}\n  {e}")
                Path(f"{len(failed)}.cmake").write_text(contents)

            i += 1
    except KeyboardInterrupt:
        Path("CMakeLists.txt").write_text(contents)
        print(name, version, path)
        print("Failed on", i)
        raise

    for s in failed:
        print(s)
