# Parent class
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        try:    
            raise NotImplementedError("Subclass must implement this method")
        except:
            print("The error handled successfully and executing speak fns from subclasses")    

# Child class
class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

# Usage
animal = Animal("lion")
dog = Dog("Buddy")
cat = Cat("Whiskers")
print(animal.speak())
print(dog.speak())  # Buddy says Woof!
print(cat.speak())  # Whiskers says Meow!