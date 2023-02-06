# Directories
OUTDIR = out
SRCDIR = ai

CDIR = $(OUTDIR)/c
CXXDIR = $(OUTDIR)/cpp
LNDIR = $(OUTDIR)/ln

DIRS = $(CDIR) $(CXXDIR) $(LNDIR)

CPP_SRCS = $(wildcard $(SRCDIR)/*.cpp)
CPP_EXES = $(CPP_SRCS:$(SRCDIR)/%.cpp=$(CXXDIR)/%.out)

C_SRCS = $(wildcard $(SRCDIR)/*.c)
C_EXES = $(C_SRCS:$(SRCDIR)/%.c=$(CDIR)/%.out)

TO_LINK = $(wildcard $(SRCDIR)/*.py) $(wildcard $(SRCDIR)/*.js)
LINKS = $(TO_LINK:$(SRCDIR)/%=$(LNDIR)/%)

EXES = $(CPP_EXES) $(C_EXES)

# Commands
CXX = g++
CXXFLAGS = -ansi -Wall -pedantic -std=c++11 -O3

CC = gcc
CCFLAGS = -Wall -O3

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

$(LNDIR)/%: $(SRCDIR)/% | $(LNDIR)
	$(LN) $< $@

$(DIRS): 
	mkdir -p $@

clean:
	$(RM) -r $(OUTDIR)