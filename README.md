nftables-graph
======================

Tools for nftables to generate call graph.

Test Command
---------------------

Generate nftables graph to svg file.

```
$ cat example.txt | ./nftables-graph.py > a.dot
$ dot -Tsvg a.dot -o a.svg
```
