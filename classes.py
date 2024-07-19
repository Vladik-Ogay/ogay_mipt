from abc import ABC, abstractmethod
import re

class Command(ABC):
    @abstractmethod
    def execute(self, interpreter):
        pass

class LoadCommand(Command):
    def __init__(self, expression):
        self.expression = expression
    
    def execute(self, interpreter):
        interpreter.registers['ACC'] = interpreter.evaluate_expression(self.expression)
        interpreter.debug_registers()

class StoreCommand(Command):
    def __init__(self, variable):
        self.variable = variable
    
    def execute(self, interpreter):
        interpreter.registers[self.variable] = interpreter.registers['ACC']
        interpreter.debug_registers()

class AndCommand(Command):
    def __init__(self, expression):
        self.expression = expression
    
    def execute(self, interpreter):
        interpreter.registers['ACC'] &= interpreter.evaluate_expression(self.expression)
        interpreter.debug_registers()

class OrCommand(Command):
    def __init__(self, expression):
        self.expression = expression
    
    def execute(self, interpreter):
        interpreter.registers['ACC'] |= interpreter.evaluate_expression(self.expression)
        interpreter.debug_registers()

class AddCommand(Command):
    def __init__(self, expression):
        self.expression = expression
    
    def execute(self, interpreter):
        interpreter.registers['ACC'] += interpreter.evaluate_expression(self.expression)
        interpreter.debug_registers()

class SubCommand(Command):
    def __init__(self, expression):
        self.expression = expression
    
    def execute(self, interpreter):
        interpreter.registers['ACC'] -= interpreter.evaluate_expression(self.expression)
        interpreter.debug_registers()

class NotCommand(Command):
    def execute(self, interpreter):
        interpreter.registers['ACC'] = not interpreter.registers['ACC']
        interpreter.debug_registers()

class SCommand(Command):
    def __init__(self, variable):
        self.variable = variable
    
    def execute(self, interpreter):
        if interpreter.registers['ACC']:
            interpreter.registers[self.variable] = True
        interpreter.debug_registers()

class RCommand(Command):
    def __init__(self, variable):
        self.variable = variable
    
    def execute(self, interpreter):
        if interpreter.registers['ACC']:
            interpreter.registers[self.variable] = False
        interpreter.debug_registers()

class JmpCommand(Command):
    def __init__(self, label):
        self.label = label
    
    def execute(self, interpreter):
        interpreter.program_counter = interpreter.labels[self.label] - 1
        interpreter.debug_registers()

class JmpcCommand(Command):
    def __init__(self, label):
        self.label = label
    
    def execute(self, interpreter):
        if interpreter.registers['ACC']:
            interpreter.program_counter = interpreter.labels[self.label] - 1
        interpreter.debug_registers()

class JmpncCommand(Command):
    def __init__(self, label):
        self.label = label
    
    def execute(self, interpreter):
        if not interpreter.registers['ACC']:
            interpreter.program_counter = interpreter.labels[self.label] - 1
        interpreter.debug_registers()

class ILParser:
    def parse(self, line):
        parts = line.split()
        command = parts[0]
        args = parts[1:]
        
        if command == 'LD':
            return LoadCommand(args[0])
        elif command == 'ST':
            return StoreCommand(args[0])
        elif command == 'AND':
            return AndCommand(args[0])
        elif command == 'OR':
            return OrCommand(args[0])
        elif command == 'ADD':
            return AddCommand(args[0])
        elif command == 'SUB':
            return SubCommand(args[0])
        elif command == 'NOT':
            return NotCommand()
        elif command == 'S':
            return SCommand(args[0])
        elif command == 'R':
            return RCommand(args[0])
        elif command == 'JMP':
            return JmpCommand(args[0])
        elif command == 'JMPC':
            return JmpcCommand(args[0])
        elif command == 'JMPNC':
            return JmpncCommand(args[0])
        else:
            raise ValueError(f"Unknown instruction {command}")


class ILInterpreter:
    def __init__(self):
        self.registers = {}
        self.program = []
        self.program_counter = 0
        self.labels = {}
        self.parser = ILParser()
    
    def load_program(self, program):
        lines = [line.strip() for line in program.split('\n') if line.strip()]
        for idx, line in enumerate(lines):
            if ':' in line:
                label, line = line.split(':', 1)
                self.labels[label.strip()] = len(self.program)
                line = line.strip()
            if line:
                self.program.append(self.parser.parse(line))
    
    def run(self):
        while self.program_counter < len(self.program):
            command = self.program[self.program_counter]
            command.execute(self)
            self.program_counter += 1
    
    def evaluate_expression(self, expression):
        # Оценка выражения: преобразование строки в число или чтение значения регистра
        if expression.isdigit():
            return int(expression)
        elif expression.startswith('16#'):
            return int(expression[3:], 16)
        elif expression in self.registers:
            return self.registers[expression]
        else:
            raise ValueError(f"Unknown expression: {expression}")
    
    def debug_registers(self):
        print(f"Registers: {self.registers}")