from il_interpreter import ILInterpreter

def run_test(program, expected_registers):
    interpreter = ILInterpreter()
    interpreter.load_program(program)
    interpreter.run()
    for register, expected_value in expected_registers.items():
        actual_value = interpreter.registers.get(register)
        assert actual_value == expected_value, f"Register {register}: expected {expected_value}, got {actual_value}"
    print(f"Test passed for program:\n{program}")

def test_load_store():
    program = """
    LD 5
    ST A
    """
    expected_registers = {'A': 5}
    run_test(program, expected_registers)

def test_set_reset():
    program = """
    LD 1
    S X
    R Y
    """
    expected_registers = {'X': True, 'Y': False}
    run_test(program, expected_registers)

def test_logical_operations():
    program = """
    LD 16#F0
    AND 16#0F
    ST A
    LD 16#F0
    ANDN 16#0F
    ST B
    LD 16#F0
    OR 16#0F
    ST C
    LD 16#F0
    ORN 16#0F
    ST D
    LD 16#F0
    XOR 16#FF
    ST E
    LD 16#F0
    XORN 16#FF
    ST F
    LD 1
    NOT
    ST G
    """
    expected_registers = {
        'A': 0,
        'B': 240,
        'C': 255,
        'D': 4294967280,
        'E': 15,
        'F': 4294967280,
        'G': 4294967294
    }
    run_test(program, expected_registers)

def test_arithmetic_operations():
    program = """
    LD 10
    ADD 5
    ST A
    LD 10
    SUB 3
    ST B
    LD 2
    MUL 4
    ST C
    LD 20
    DIV 4
    ST D
    LD 20
    MOD 3
    ST E
    """
    expected_registers = {
        'A': 15,
        'B': 7,
        'C': 8,
        'D': 5,
        'E': 2
    }
    run_test(program, expected_registers)

def test_control_flow():
    program = """
    LD 1
    JMP Skip
    LD 0
    ST A
    Skip: LD 1
    ST B
    LD 1
    JMPC Done
    LD 0
    ST C
    Done: LD 1
    ST D
    LD 0
    JMPNC End
    LD 0
    ST E
    End: LD 1
    ST F
    """
    expected_registers = {
        'A': None,  # Эта команда не должна выполниться
        'B': 1,
        'C': None,  # Эта команда не должна выполниться
        'D': 1,
        'E': None,  # Эта команда не должна выполниться
        'F': 1
    }
    run_test(program, expected_registers)

if __name__ == "__main__":
    test_load_store()
    test_set_reset()
    test_logical_operations()
    test_arithmetic_operations()
    test_control_flow()
    print("All tests passed")
