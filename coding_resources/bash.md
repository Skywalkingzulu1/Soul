# Bash/Shell Quick Reference

## Basics
```bash
#!/bin/bash

# Variables
name="Alice"
age=25

# Print
echo "Hello, $name!"
echo "You are $age years old"

# Input
read -p "Enter your name: " name
```

## Variables
```bash
# Basic assignment
name="Alice"
age=25

# Read-only
readonly PI=3.14159

# Environment variables
export PATH=$PATH:/new/path

# Command substitution
current_date=$(date)
files=$(ls)
```

## Control Flow
```bash
# If-else
if [ $age -lt 18 ]; then
    echo "Minor"
elif [ $age -eq 18 ]; then
    echo "Just became adult"
else
    echo "Adult"
fi

# Case statement
case $day in
    1) echo "Monday" ;;
    2) echo "Tuesday" ;;
    *) echo "Other day" ;;
esac
```

## Loops
```bash
# For loop
for i in {1..5}; do
    echo $i
done

# For loop with list
for file in *.txt; do
    echo "File: $file"
done

# While loop
count=0
while [ $count -lt 5 ]; do
    echo $count
    count=$((count + 1))
done
```

## Functions
```bash
# Function definition
function greet() {
    echo "Hello, $1!"
}

# Or
greet() {
    echo "Hello, $1!"
}

# Call function
greet "Alice"

# Return value
get_sum() {
    echo $(( $1 + $2 ))
}
result=$(get_sum 5 3)
```

## File Operations
```bash
# Read file
while read line; do
    echo "$line"
done < file.txt

# Write to file
echo "Hello" > output.txt
echo "Append" >> output.txt

# Check file
if [ -f file.txt ]; then
    echo "File exists"
fi

if [ -d dir ]; then
    echo "Directory exists"
fi
```

## Common Commands
```bash
# Files
ls -la
mkdir -p newdir
rm -rf dir
cp -r source dest
mv old new

# Text processing
grep "pattern" file
sed 's/old/new/g' file
awk '{print $1}' file

# System
ps aux
top
kill pid
df -h
```

## String Operations
```bash
# Length
${#string}

# Substring
${string:0:5}

# Replace
${string/old/new}

# Array
arr=(one two three)
echo ${arr[0]}
echo ${arr[@]}
```