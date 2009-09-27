// Copyright 2008 Janusz Skonieczny.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/* 
 * Ajax navigation support, initlializes the history jQuery plugin
 *
 * The history plugin works as a middleware between navigation 
 * requests and actual response loading. It does not handle urls requested 
 * nor executing requests and loading responces.
 * 
 * It only does handle browser history operations, if you whant something 
 * to be visible as history element you have to put it there, also
 * you need to handle actual navigation when history get's traversed.
 *
 * You have to catch navigation requests, change tem into some form 
 * unique keyword that you can uderstand when you'll have to load 
 * resources for this keyword.  
 */

var non_ajax_url_prefix_re = /^.*school/;
var rpc_url_prefix = '/school';
var content_selector = "#content";

function InitAjaxNaviation(){
  $.history.init(HistoryNavigateTo);
  $(content_selector).ajaxError(NavigationError);  
}
$(document).ready(InitAjaxNaviation);

/* 
 * Adds given url to history - will get loaded by the history plugin other end.
 */ 
function NavigateTo(url, alreadyLoaded ){
  // instead acctually going to the URL, pass the link to the history plugin
  // extract the url part that become a hash part for the current url  
  $.history.load(url.replace(non_ajax_url_prefix,''), alreadyLoaded);
}
 
/* 
 * Replaces default link navigation operation with history plugin based navigation.
 * Bind it to to the click event on links.
 */ 
function NavigateLink(e) {
  console.debug(e) ;
  NavigateTo(this.href, false); 
  e.preventDefault();
}

/* 
 * The history plugin backend for loading resources.
 */
function HistoryNavigateTo(keyword, alreadyLoaded){
  console.debug("HistoryNavigateTo: "+keyword);
  if (keyword == null || keyword =='' || keyword == '/'){
    // if keyword is empty, were in location without hash
    // instead accually loading a default resource make it a position 
    // in bowser history, this will result in calling this function again
    //$.history.load('/issues/my/'); 
    return;
  }
  if (alreadyLoaded != true){
    // load resources for that browser history keyword
    $(content_selector).load(rpc_url_prefix + keyword, null, function(responseText, textStatus, xhr){
        // perform a post load processing on loaded content.
        // error handling is done in NavigationError
        HtmlContentPostLoadPorocessing();          
      });
  } else {
    // an actual load happened somewhere else, we'll nedd only to post-process.
    HtmlContentPostLoadPorocessing()
  }
}

/*
 * Ajax error handling
 */
function NavigationError(event, xhr, settings){
   console.debug('NavigationError: ajax load failed, redirecting...', settings);
   // in case of an error, redirect to show the error page.
   // document.location.href = settings.url;
   document.write(xhr.responseText);
   return false;
}

/*
 * All loaded HTML need't to be processed
 */
function HtmlContentPostLoadPorocessing(){
    //TODO: throw it off somewhere
  $(content_selector+" textarea").autogrow();
  $(content_selector+" a").click(NavigateLink);
  // update the page title 
  document.title = $(content_selector+" title").text() + " | School";
  // this will not acually load page but will 
  // ensure that page title in history is current
  window.location.replace(window.location); 
}