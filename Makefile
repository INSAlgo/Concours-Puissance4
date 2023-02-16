# Directories
OUTDIR = out
SRCDIR = test-ai

CDIR = $(OUTDIR)/c
CXXDIR = $(OUTDIR)/cpp
LNDIR = $(OUTDIR)/ln
JAVADIR = $(OUTDIR)/java

DIRS = $(CDIR) $(CXXDIR) $(JAVADIR) $(LNDIR)

CPP_SRCS = $(wildcard $(SRCDIR)/*.cpp)
CPP_EXES = $(CPP_SRCS:$(SRCDIR)/%.cpp=$(CXXDIR)/%.out)

C_SRCS = $(wildcard $(SRCDIR)/*.c)
C_EXES = $(C_SRCS:$(SRCDIR)/%.c=$(CDIR)/%.out)

JAVA_SRCS = $(wildcard $(SRCDIR)/*.java)
JAVA_EXES = $(JAVA_SRCS:$(SRCDIR)/%.java=$(JAVADIR)/%.class)

TO_LINK = $(wildcard $(SRCDIR)/*.py) $(wildcard $(SRCDIR)/*.js)
LINKS = $(TO_LINK:$(SRCDIR)/%=$(LNDIR)/%)

EXES = $(CPP_EXES) $(C_EXES) $(JAVA_EXES)

# Commands
CXX = g++
CXXFLAGS = -ansi -Wall -pedantic -std=c++11 -O3

CC = gcc
CCFLAGS = -Wall -O3

JAVAC = javac

LN = ln

RM = rm -f
ECHO = echo

.PHONY: all clean fclean re run debug

$(info $$EXES is $(TO_LINK))
all: $(EXES) $(LINKS)

$(CDIR)/%.out: $(SRCDIR)/%.c | $(CDIR)
	$(CC) $(CCFLAGS) -o $@ $<

$(CXXDIR)/%.out: $(SRCDIR)/%.cpp | $(CXXDIR)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(JAVADIR)/%.class: $(SRCDIR)/%.java | $(JAVADIR)
	$(JAVAC) -d $(JAVADIR) $<

$(LNDIR)/%: $(SRCDIR)/% | $(LNDIR)
	$(LN) $< $@

$(DIRS): 
	mkdir -p $@

clean:
	$(RM) -r $(OUTDIR)
