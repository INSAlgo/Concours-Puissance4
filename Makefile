# Directories
OUTDIR = out
SRCDIR = test-ai

CDIR = $(OUTDIR)/c
CXXDIR = $(OUTDIR)/cpp
LNDIR = $(OUTDIR)/ln
JAVADIR = $(OUTDIR)/java
CSDIR = $(OUTDIR)/cs
RSDIR = $(OUTDIR)/rs

CPP_SRCS = $(wildcard $(SRCDIR)/*.cpp)
CPP_EXES = $(CPP_SRCS:$(SRCDIR)/%.cpp=$(CXXDIR)/%.out)

C_SRCS = $(wildcard $(SRCDIR)/*.c)
C_EXES = $(C_SRCS:$(SRCDIR)/%.c=$(CDIR)/%.out)

RS_SRCS = $(wildcard $(SRCDIR)/*.rs)
RS_EXES = $(RS_SRCS:$(SRCDIR)/%.rs=%)

CARGO_TOML = Cargo.toml

JAVA_SRCS = $(wildcard $(SRCDIR)/*.java)
JAVA_EXES = $(JAVA_SRCS:$(SRCDIR)/%.java=$(JAVADIR)/%.class)

CS_SRCS = $(wildcard $(SRCDIR)/*.cs)
CS_DIRS = $(CS_SRCS:$(SRCDIR)/%.cs=$(SRCDIR)/%)
CS_NEW_SRCS = $(foreach dir, $(CS_DIRS), $(dir)/$(dir:$(SRCDIR)/%=%.cs))
CS_PROJS = $(foreach dir, $(CS_DIRS), $(dir)/$(dir:$(SRCDIR)/%=%.csproj))
# CS_EXES = $(foreach dir, $(CS_DIRS), $(CSDIR)/$(dir:$(SRCDIR)/%=%)/$(dir:$(SRCDIR)/%=%))
CS_EXES = $(CS_SRCS:$(SRCDIR)/%.cs=$(CSDIR)/%build)
BASE_CSPROJ_FILE = base.csproj

TO_LINK = $(wildcard $(SRCDIR)/*.py) $(wildcard $(SRCDIR)/*.js)
LINKS = $(TO_LINK:$(SRCDIR)/%=$(LNDIR)/%)

EXES = $(CPP_EXES) $(C_EXES) $(JAVA_EXES) $(CS_EXES)

DIRS = $(CDIR) $(CXXDIR) $(JAVADIR) $(LNDIR) $(CSDIR) $(CS_DIRS) $(RSDIR)

# Commands
CXX = g++
CXXFLAGS = -ansi -Wall -pedantic -std=c++11 -O3

CC = gcc
CCFLAGS = -Wall -O3

JAVAC = javac

RSBUILD = cargo build
RSFLAGS = --release

LN = ln

RM = rm -f
ECHO = echo

CS = dotnet
BUILD = publish

.PHONY: all clean fclean re run debug rust cargo_toml

$(info $$EXES is $(CS_EXES))
all: $(EXES) $(LINKS) rust

$(CDIR)/%.out: $(SRCDIR)/%.c | $(CDIR)
	- $(CC) $(CCFLAGS) -o $@ $<

$(CXXDIR)/%.out: $(SRCDIR)/%.cpp | $(CXXDIR)
	- $(CXX) $(CXXFLAGS) -o $@ $<

$(JAVADIR)/%.class: $(SRCDIR)/%.java | $(JAVADIR)
	- $(JAVAC) -d $(JAVADIR) $<

rust: cargo_toml | $(RSDIR)
	- $(RSBUILD) $(RSFLAGS)
	$(foreach O, $(RS_EXES), cp target/release/$(O) $(RSDIR)/$(O) &)
	$(RM) -r target

cargo_toml:
	$(file > $(CARGO_TOML), [package])
	$(file >> $(CARGO_TOML), name = "out-rs")
	$(file >> $(CARGO_TOML), version = "0.1.0")
	$(file >> $(CARGO_TOML), edition = "2018")
	$(file >> $(CARGO_TOML), [dependencies])
	$(file >> $(CARGO_TOML), rand = "0.8.4")
	$(file >> $(CARGO_TOML)) $(foreach O, $(RS_SRCS), $(file >> $(CARGO_TOML), [[bin]]) $(file >> $(CARGO_TOML), path = "$O") $(file >> $(CARGO_TOML), $(O:$(SRCDIR)/%.rs=name = "%")))

$(CSDIR)/%build: $(SRCDIR)/%csproj $(SRCDIR)/%cs | $(CSDIR)
	- $(CS) $(BUILD) -o $(@:$(CSDIR)/%build=$(CSDIR)/%) $(SRCDIR)/$(@:$(CSDIR)/%build=%)/$(@:$(CSDIR)/%build=%).csproj
	$(RM) -r $(SRCDIR)/$(@:$(CSDIR)/%build=%)

$(SRCDIR)/%csproj: $(BASE_CSPROJ_FILE) | $(CS_DIRS)
	$(LN) -f $< $(SRCDIR)/$(@:$(SRCDIR)/%csproj=%)/$(@:$(SRCDIR)/%csproj=%).csproj
	
$(SRCDIR)/%cs: $(SRCDIR)/%.cs | $(CS_DIRS)
	$(LN) -f $< $(SRCDIR)/$(@:$(SRCDIR)/%cs=%)/$(@:$(SRCDIR)/%cs=%).cs

$(LNDIR)/%: $(SRCDIR)/% | $(LNDIR)
	$(LN) $< $@

$(DIRS): 
	mkdir -p $@

clean:
	$(RM) -r $(OUTDIR)
	$(RM) $(CARGO_TOML)
	$(RM) Cargo.lock
