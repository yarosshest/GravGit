import zlib
import binascii
from pathlib import Path
import graphviz as gv
from hashlib import sha1
import re
# output all files in directory

types = [b'blob', b'tree', b'commit']
child = [b'100644', b'100755', b'040000', b'160000', b'120000']
splitNames = re.compile(b"(100644|100755|40000|160000|120000)(.*?)(\\x00)")
splitHash = re.compile(b"(\\x00)([\\s\\S]*?)(100644|100755|40000|160000|120000|$)")

def parseTree(tree):
    res = re.findall(splitNames, tree)
    names = list(map(lambda x: x[1], res))
    clas = list(map(lambda x: x[0], res))

    res = re.findall(splitHash, tree)
    hashes = list(map(lambda x: x[1], res))

    while b'' in hashes:
        hashes.remove(b'')

    hashes = list(map(lambda x: binascii.b2a_hex(x), hashes))

    return list(zip(names, hashes, clas))


def terType(ter):
    if ter.startswith(types[0]):
        return "blob"
    elif ter.startswith(types[1]):
        return "tree"
    elif ter.startswith(types[2]):
        return "commit"


def commitGetTree(commit):
    for line in commit.split(b"\n"):
        return line.split(b" ")[2]

def commitGetComment(commit):
    line = commit.split(b"\n")
    while b'' in line:
        line.remove(b'')
    return line[-1]

def commitGetParent(commit):
    for line in commit.split(b"\n"):
        if line.startswith(b"parent"):
            return line.split(b" ")[1]
    else:
        return None


def treeGetTree(tree):
    res = re.split(b"\\x00", tree)
    pass


def list_files(directory):
    for i in directory.iterdir():
        for file in i.iterdir():
            print(file)
            compressed_contents = open(file, 'rb').read()
            decompressed_contents = zlib.decompressobj().decompress(compressed_contents)
            print(decompressed_contents)
            obj = terType(decompressed_contents)
            print(f"Type: {obj}")
            if obj == "commit":
                print(f"Tree: {commitGetTree(decompressed_contents).decode('utf-8')}")
                if commitGetParent(decompressed_contents) is not None:
                    print(f"Parent: {commitGetParent(decompressed_contents).decode('utf-8')}")
            elif obj == "tree":
                for i in parseTree(decompressed_contents):
                    print(f'Name: {i[0]} Hash: {i[1]}')
            elif obj == "blob":
                pass

            print(f"hash: {sha1(decompressed_contents).hexdigest()}")
            print("\n")


# output graphviz
def graphviz(directory):
    dot = gv.Digraph()
    for i in directory.iterdir():
        for file in i.iterdir():
            compressed_contents = open(file, 'rb').read()
            decompressed_contents = zlib.decompressobj().decompress(compressed_contents)
            obj = terType(decompressed_contents)
            if obj == "commit":
                dot.node(sha1(decompressed_contents).hexdigest(),
                         label=sha1(decompressed_contents).hexdigest()+"\n"+obj+"\n"+commitGetComment(decompressed_contents).decode('utf-8'))
                dot.edge(sha1(decompressed_contents).hexdigest(), commitGetTree(decompressed_contents).decode("utf-8"))
                if commitGetParent(decompressed_contents) is not None:
                    dot.edge(sha1(decompressed_contents).hexdigest(),
                             commitGetParent(decompressed_contents).decode("utf-8"))
            elif obj == "tree":
                dot.node(sha1(decompressed_contents).hexdigest(), label=sha1(decompressed_contents).hexdigest()+"\n"+obj)
                for i in parseTree(decompressed_contents):
                    dot.edge(sha1(decompressed_contents).hexdigest(), i[1].decode("utf-8"))
                    if i[2] == b'100644':
                        dot.node(i[1].decode("utf-8"), label=i[1].decode("utf-8")+"\n"+"blob"+"\n"+i[0].decode("utf-8"))
    dot.render('test-output/round-table.gv', view=True)


if __name__ == '__main__':
    Path = Path(__file__).parent
    Path = Path.joinpath(Path, 'output/.git/objects/')
    # print(binascii.b2a_hex((b'\x99$\x95\xea\xea0\xccD\x0b\x85\xf4\xedJ\xafI\nyE\x11[')))
    list_files(Path)
    graphviz(Path)