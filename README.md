## Plop

Plop is a dead-simple
[concatenative programming language](https://en.wikipedia.org/wiki/Concatenative_programming_language)
inspired by [Forth](https://www.forth.com/forth/),
and [Porth](https://gitlab.com/tsoding/porth).

It essentially aims to be like Forth, but with a much more limited set of features and with C-style braces.

WARNING: This language is currently unstable. No guarantees regarding the functionality or stability of this project can be made as of now.

## Usage

### Run Plop File

```bash
$ ./plop.py <input-file>
```

## Testing

### Run Test Suite

```bash
$ ./run_tests.py
```

## Examples

### Hello World

```py
"Hello, world!" println
```

### Count to Ten

```py
0 dup 10 = not while {
    1 +
    dup println
    dup 10 = not
}
```

### Say Hello

```py
proc say-hello {
    "Hello, " print
    print
    "!" println
}

"Please enter your name: " print
read say-hello
```

## Language Reference

WARNING: This language is currently unstable. The features listed below may be subject to change in the future.

### Literals

Literals are constant values, which, when encountered in source code are pushed
to the top of the data stack for later use. Plop currently only supports 3
literal types: integers, strings, and booleans.

#### Integers

Integer literals are words that consist only of decimal digits (0..9). When
encountered, integer literals will be pushed to the top of the data-stack for
later use.

```py
# Push the numbers 10 and 5 onto the data stack, then add them together. 
10 5 +
```

#### Strings

String literals are any sequence of characters placed between a pair of 
double-quotes ("").

Strings may also include escape sequences--a character preceded by a backslash
used to represent non-visible characters. The following escape sequences are
currently supported:

- `\n` - new line
- `\r` - carriage return
- `\t` - tab

```py
# Push the string "Hello, world!" onto the data stack, then print it.
"Hello, world!" println
```

#### Booleans

Boolean literals can be pushed onto the data-stack my means of using one of two
words: `true` or `false`. When these words are encountered, their respective
boolean values are pushed to the top of the data stack.

```py
# Push the boolean values `true` and `false` to the data stack, then perform a
# logical and operation on them
true false and
```

### Intrinsics

TODO...

### Control Flow

TODO...

## Contributing

Please feel free to contribute if you're interesting in doing so!

PRs are very much welcome <3

## License

Plop is MIT licensed. See [LICENSE](LICENSE) for more info!
