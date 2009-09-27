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


/**
 * Document initializaction 
 */
function DocumentInit(){
  InitConsole()
  ModernBrowserCheck();
  console.debug("document.ready init completed");  
}
$(document).ready(DocumentInit); 

/**
 * Post a form
 */
function InitConsole(){
  if (window.console && window.console.debug){
    console.debug("Console already is");
    return;
  }
  window.console = {};
  window.console.debug = function(str){};
  // sorry no logging today :(
}

function ModernBrowserCheck(){
  if(!jQuery.support.boxModel){
      new Boxy("#browser-upgrade",{title:"Oh no!", modal: true})
    }
 }

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
function InitAjaxNaviation(){
  $.history.init(HistoryNavigateTo);
  $("#main").ajaxError(NavigationError);  
}
$(document).ready(InitAjaxNaviation);

/* 
 * Adds given url to history - will get loaded by the history plugin other end.
 */ 
function NavigateTo(url, alreadyLoaded ){
  // instead acctually going to the URL, pass the link to the history plugin
  // extract the url part that become a hash part for the current url  
  $.history.load(url.replace(/^.*tbd/,''), alreadyLoaded);  
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
    $.history.load('/issues/my/'); 
    return;
  }
  if (alreadyLoaded != true){
    // load resources for that browser history keyword
    $("#main").load('/tbd' + keyword, null, function(responseText, textStatus, xhr){
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
  $("#main textarea").autogrow();
  $("#main a").click(NavigateLink);
  // update the page title 
  document.title = $("#main title").text() + " | ToBeDone";
  // this will not acually load page but will 
  // ensure that page title in history is current
  window.location.replace(window.location); 
}

/* 
 * Special form load postprocessing.
 */
function InitForm(){
  $('#main form').ajaxForm({
            target: '#main',
            complete: PostSubmitHistoryUpdate,
            b2eforeSend: function(xhr){ xhr.onreadystatechange = function(x){
              console.debug(x.target.readyState); 
              console.debug(x); 
              console.debug(x.currentTarget.getResponseHeader("Location"));} 
              },
            s2uccess: function (data, textStatus) {
              console.debug(data); 
              console.debug(textStatus); 
              }
        });
  console.debug("InitForm completed");  
}

/*
 * Updates history after form is saved and request redirectred.
 * It creates a history item with current location.
 */
function PostSubmitHistoryUpdate(xhr, textStatus, options) {

  if (textStatus == 'error'){
    return;
  }
  var currentLocation = xhr.getResponseHeader("X-Current-Location")
  console.debug("X-Current-Location: " + currentLocation)
  if (currentLocation != null) {
    NavigateTo(currentLocation, true);
  }
  console.debug(xhr)  
}

function InitIssueForm() {
    $('#id_follow_up').datepicker({ dateFormat: 'yy-mm-dd' });
    $('#id_project').load('/tbd/rpc/projects/?type=options', null, function(responseText, textStatus, xhr) {
        $('#id_project').prepend('<option selected="true">----</option>');
    }).bind('change', {}, function(e) {
        console.debug('select');
        $('#id_feature').load('/tbd/rpc/features/?type=options&project=' + $('#id_project').val(), null, function(responseText, textStatus, xhr) {
            $('#id_feature').prepend('<option selected="true">----</option>');
        });
    });
    var options = {
        target: '#issue-form',
        complete: IssueFormSubmitComlepted
    }
    $('#main form').submit(function() {
        $(this).ajaxSubmit(options);
        return false;
    });
    $('#save-and-add-more').click(function() {
        options.complete = function(xhr, textStatus, options) {
            if (IssueFormSubmitComlepted(xhr, textStatus, options)) {
                //$('#new-issue').click();
            }
        };
        $(this).ajaxSubmit(options);
        return false;
    });
}

function IssueFormSubmitComlepted(xhr, textStatus, options) {
    if (textStatus == 'error') {
        return false;
    }
    $('.data-table table').append(xhr.responseText);
    if ($('.data-table table'))
    $('#issue-form').empty();
    return true;
}

function InitMenu() {
    $.get(project_list_rpc_url, null, function(data, textStatus) {
        console.info(textStatus + ' ' + data);
        $('#projects').hide().prepend(data);
        $("#menu a").click(NavigateLink);
        $('#projects').slideDown('slow');
        $("#new-issue").unbind('click');
        $("#new-issue").click(function(e) {
            listHeader = $("#issue-form");
            if (listHeader.size() > 0){   
                listHeader.load(issue_new_url, null, function(responseText, textStatus, xhr) {
                    HtmlContentPostLoadPorocessing();

                });
            } else {
                alert("TODO: Navigacja do listy issues zgodnie z kontekstem");
            }
            e.preventDefault();
        });
    });
}