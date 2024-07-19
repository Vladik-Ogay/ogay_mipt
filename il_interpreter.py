from abc import ABC, abstractmethod
import re

class Command(ABC):
    @abstractmethod
    def execute(self, interpreter: 'ILInterpreter') -> None:
        pass

def debug_decorator(func):
    def wrapper(self, interpreter):
        result = func(self, interpreter)
        interpreter.debug_registers()
        return result
    return wrapper

class LoadCommand(Command):
    def __init__(self, expression: str) -> None:
        self.expression = expression
    
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        interpreter.registers['ACC'] = interpreter.evaluate_expression(self.expression) & 0xFFFFFFFF

class StoreCommand(Command):
    def __init__(self, variable: str) -> None:
        self.variable = variable
    
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        interpreter.registers[self.variable] = interpreter.registers['ACC']

class BinaryCommand(Command):
    def __init__(self, expression: str) -> None:
        self.expression = expression
    
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        value = interpreter.evaluate_expression(self.expression) & 0xFFFFFFFF
        self.apply_operation(interpreter, value)
        interpreter.registers['ACC'] &= 0xFFFFFFFF
    
    @abstractmethod
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        pass

class AndCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        result = interpreter.registers['ACC'] & value
        interpreter.registers['ACC'] = result & 0xFFFFFFFF

class OrCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        result = interpreter.registers['ACC'] | value
        interpreter.registers['ACC'] = result & 0xFFFFFFFF

class AddCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        result = interpreter.registers['ACC'] + value
        interpreter.registers['ACC'] = result & 0xFFFFFFFF

class SubCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        result = interpreter.registers['ACC'] - value
        interpreter.registers['ACC'] = result & 0xFFFFFFFF

class NotCommand(Command):
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        result = ~interpreter.registers['ACC']
        interpreter.registers['ACC'] = result & 0xFFFFFFFF

class ConditionalCommand(Command):
    def __init__(self, variable: str) -> None:
        self.variable = variable

    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        if interpreter.registers['ACC']:
            self.apply_operation(interpreter)

    @abstractmethod
    def apply_operation(self, interpreter: 'ILInterpreter') -> None:
        pass

class SCommand(ConditionalCommand):
    def apply_operation(self, interpreter: 'ILInterpreter') -> None:
        interpreter.registers[self.variable] = True

class RCommand(ConditionalCommand):
    def apply_operation(self, interpreter: 'ILInterpreter') -> None:
        interpreter.registers[self.variable] = False

class JmpCommand(Command):
    def __init__(self, label: str) -> None:
        self.label = label
    
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        interpreter.program_counter = interpreter.labels[self.label] - 1

class JmpcCommand(JmpCommand):
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        if interpreter.registers['ACC']:
            interpreter.program_counter = interpreter.labels[self.label] - 1

class JmpncCommand(JmpCommand):
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        if not interpreter.registers['ACC']:
            interpreter.program_counter = interpreter.labels[self.label] - 1

class NotBinaryCommand(BinaryCommand):
    @debug_decorator
    def execute(self, interpreter: 'ILInterpreter') -> None:
        value = interpreter.evaluate_expression(self.expression) & 0xFFFFFFFF
        print(f"Evaluating expression: {self.expression}, value: {value}")
        self.apply_operation(interpreter, value)

class AndnCommand(NotBinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        inverted_value = ~value & 0xFFFFFFFF
        result = (interpreter.registers['ACC'] & inverted_value) & 0xFFFFFFFF
        interpreter.registers['ACC'] = result

class OrnCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        inverted_value = ~value & 0xFFFFFFFF  # Инвертируем второй операнд
        result = interpreter.registers['ACC'] | inverted_value  # Применяем OR
        interpreter.registers['ACC'] = result & 0xFFFFFFFF  # Применяем маску

class XorCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        interpreter.registers['ACC'] ^= value

class XornCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        inverted_value = ~value & 0xFFFFFFFF  # Инвертируем второй операнд
        result = interpreter.registers['ACC'] ^ inverted_value  # Применяем XOR
        interpreter.registers['ACC'] = result & 0xFFFFFFFF  # Применяем маску

class MulCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        interpreter.registers['ACC'] *= value

class DivCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        interpreter.registers['ACC'] //= value

class ModCommand(BinaryCommand):
    def apply_operation(self, interpreter: 'ILInterpreter', value: int) -> None:
        interpreter.registers['ACC'] %= value

class ILParser:
    def parse(self, line: str) -> Command:
        parts = line.split()
        command = parts[0]
        args = parts[1:]
        
        command_map = {
            'LD': LoadCommand,
            'ST': StoreCommand,
            'AND': AndCommand,
            'ANDN': AndnCommand,
            'OR': OrCommand,
            'ORN': OrnCommand,
            'XOR': XorCommand,
            'XORN': XornCommand,
            'ADD': AddCommand,
            'SUB': SubCommand,
            'MUL': MulCommand,
            'DIV': DivCommand,
            'MOD': ModCommand,
            'NOT': NotCommand,
            'S': SCommand,
            'R': RCommand,
            'JMP': JmpCommand,
            'JMPC': JmpcCommand,
            'JMPNC': JmpncCommand
        }

        if command in command_map:
            return command_map[command](*args)
        else:
            raise ValueError(f"Unknown instruction {command}")

class ILInterpreter:
    def __init__(self) -> None:
        self.registers = {'ACC': 0}
        self.program = []
        self.program_counter = 0
        self.labels = {}
        self.parser = ILParser()
    
    def load_program(self, program: str) -> None:
        lines = [line.strip() for line in program.split('\n') if line.strip()]
        for idx, line in enumerate(lines):
            if ':' in line:
                label, line = line.split(':', 1)
                self.labels[label.strip()] = len(self.program)
                line = line.strip()
            if line:
                self.program.append(self.parser.parse(line))
    
    def run(self) -> None:
        while self.program_counter < len(self.program):
            command = self.program[self.program_counter]
            command.execute(self)
            self.program_counter += 1
    
    def evaluate_expression(self, expression: str) -> int:
        try:
            if expression.isdigit():
                return int(expression) & 0xFFFFFFFF
            elif expression.startswith('16#'):
                return int(expression[3:], 16) & 0xFFFFFFFF
            elif expression in self.registers:
                return self.registers[expression] & 0xFFFFFFFF
            else:
                raise ValueError(f"Unknown expression: {expression}")
        except ValueError as e:
            print(f"Error evaluating expression {expression}: {e}")
            return 0
    
    def debug_registers(self) -> None:
        self.registers = {k: v & 0xFFFFFFFF if isinstance(v, int) else v for k, v in self.registers.items()}
        print(f"Registers: {self.registers}")
