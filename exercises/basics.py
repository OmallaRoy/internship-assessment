from typing import List


def collatz(n: int) -> List[int]:

    # Initialize the list to store various collections of the integers
    integers = [n]

    # While loop that repeats provided that the  integer(n)  is not equal to  1
    while n != 1:

        # Condition(if-else) to check if the integer is odd or even.
        if n % 2 == 0:
            n = n // 2  # if the n is even,then divide it by 2
        else:
            n = n * 3 + 1  # if n is odd,then multiply by 3 and add by 1

        integers.append(n)

    return integers


def distinct_numbers(numbers: List[int]) -> int:

    # convert the list of numbers to a set to drop the duplicates
    # and convert back to list

    unique_list = list(set(numbers))
    return len(unique_list)
