import React from 'react'
import ReactDOM from 'react-dom'

import '../styles/main.scss'

import StateMap from './state-map'
import FileBrowser from './file-browser'
import StateBounds from './state-bounds'

window.STATE_BOUNDS = StateBounds;

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display = "block";
  this.style.display = "none";
}


function onFileChange() {
  if(this.files.length == 0) {
    document.querySelector(".file-name").innerHTML = "";
  } else if(this.files.length == 1) {
    document.querySelector(".file-name").innerHTML = this.files[0].name;
  } else {
    document.querySelector(".file-name").innerHTML = `${this.files.length} files`;
  }
}


function initTabs() {
  function tabClick() {
    const clicked = this.dataset.tab;
    document.querySelectorAll("[data-tabbody]").forEach(function (t) {
      if(t.dataset.tabbody === clicked) {
        t.style.display = "block";
      } else {
        t.style.display = "none"
      }
    });
    document.querySelectorAll("[data-tab]").forEach(function (t) {
      if(t.dataset.tab === clicked) {
        console.log(t.parentNode);
        t.parentNode.className = "is-active";
      } else {
        t.parentNode.className = "";
      }
    });
  }
  const tabs = document.querySelectorAll("[data-tab]");
  if(tabs.length) {
    tabs.forEach(t => t.onclick = tabClick);
    tabs[0].click();
  }
}

window.addEventListener('load', () => {
  initTabs();

  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    const states = JSON.parse(document.getElementById('state-status').textContent);
    ReactDOM.render(React.createElement(
      StateMap,
      {
        states: states,
        statuses: {
          'unknown': {'name': 'Unknown', 'fill': '#999'},
          'collection': {'name': 'Collecting', 'fill': '#6b94ae'},
          'cleaning': {'name': 'Cleaning', 'fill': '#14374e'},
          'prior-year': {'name': 'Prior Year(s)', 'fill': '#87d67f'},
          'available': {'name': 'Data Available', 'fill': '#1c6414'},
        },
        link_template: state => `/${state.toLowerCase()}`
      }),
      sm
    );
  }

  const fb = document.querySelector('[data-hook="file-browser"]');
  if (fb) {
    const files = JSON.parse(document.getElementById('files-data').textContent);
    ReactDOM.render(React.createElement(
      FileBrowser,
      {
        files: files,
        columns: files_columns,
      }),
      fb
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
  document.querySelectorAll('input[type=file]').forEach(e => e.onchange = onFileChange);
});
