max_steps = 1000
levy_factor = 1.2
pdf = [step ** (-levy_factor - 1) for step in range(1, max_steps + 1)]
print(pdf)
