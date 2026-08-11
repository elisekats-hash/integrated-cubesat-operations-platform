import matlab.engine

print("Starting MATLAB")
eng = matlab.engine.start_matlab()
print("MATLAB connected!")
result = eng.sqrt(25.0)
print("Result: ", result)
