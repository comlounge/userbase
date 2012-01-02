VERSION=2.0.0
CSS = ./../static/css/userbase.css
CSS_MIN = ./../static/css/userbase.min.css
CSS_LESS = ./userbase.less
LESS_COMPESSOR ?= `which lessc`
UGLIFY_JS ?= `which uglifyjs`
WATCHR ?= `which watchr`

build:
	@@if test ! -z ${LESS_COMPESSOR}; then \
		sed -e 's/@VERSION/'"v${VERSION}"'/' -e 's/@DATE/'"`date`"'/' <${CSS_LESS} >${CSS_LESS}.tmp; \
		lessc ${CSS_LESS}.tmp > ${CSS}; \
		lessc ${CSS_LESS}.tmp > ${CSS_MIN} --compress; \
		rm -f ${CSS_LESS}.tmp; \
		echo "CSS successfully built! - `date`"; \
	else \
		echo "You must have the LESS compiler installed in order to build the CSS."; \
		echo "You can install it by running: npm install less -g"; \
	fi

watch:
	@@if test ! -z ${WATCHR}; then \
	  echo "Watching less files..."; \
	  watchr -e "watch('.*\.less') { system 'make' }"; \
	else \
		echo "You must have the watchr installed in order to watch Bootstrap Less files."; \
		echo "You can install it by running: gem install watchr"; \
	fi

.PHONY: build watch
