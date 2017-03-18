from subprocess import call

# for i in range(1, 11):
problem = 3
for i in [1, 3, 5, 7, 8, 9, 10]:
    call(f"python run_search.py -p {problem} -s {i} > results/p{problem}_s{i}", shell=True)
