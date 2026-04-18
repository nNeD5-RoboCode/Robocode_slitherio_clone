import pstats
from pstats import SortKey

# import cProfile
# import sys
# from snake import main
#
#
# if len(sys.argv) > 2 and sys.argv[1] == "run":
#     cProfile.run("main()", "profiler_output.txt")

p = pstats.Stats("profiler_output")
p = p.strip_dirs()
p = p.sort_stats(SortKey.TIME)
p.print_stats()
