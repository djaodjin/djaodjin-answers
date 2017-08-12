/** Convienience drivers to trigger the djaodjin-answers API
 */

(function ($) {
    "use strict";

    /** Follow/Unfollow and Up/Down vote a ``Question``

        HTML requirements:

        <... class="dj-answers-actions"
          <... class="dj-answers-upvote">
          </...>
          <... class="dj-answers-downvote">
          </...>
          <... class="dj-answers-follow">
          </...>
        </...>
     */
    function ForumQuestion(el, options){
        this.element = $(el);
        this.options = options;
        this.init();
    }

    ForumQuestion.prototype = {
        init: function () {
            var self = this;
            self.element.find(".dj-answers-follow").click(function() {
                self.follow();
            });
            self.element.find(".dj-answers-unfollow").click(function() {
                self.unfollow();
            });
            self.element.find(".dj-answers-upvote").click(function() {
                self.upvote();
            });
            self.element.find(".dj-answers-downvote").click(function() {
                self.downvote();
            });
        },

        follow: function () {
            var self = this;
            $.ajax({
                type: "POST",
                url: self.options.api_follow,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", getMetaCSRFToken());
                },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    self.element.find(".dj-answers-follow").removeClass(
                        "dj-on").addClass("dj-off");
                    self.element.find(".dj-answers-unfollow").removeClass(
                        "dj-off").addClass("dj-on");
                    showMessages(
                        ['You will now receive an e-mail for new comments on "'
                        + data.title + '".'], "success");
                },
                error: function(resp) {
                    showErrorMessages(resp, "error");
                },
            });
        },

        unfollow: function () {
            var self = this;
            $.ajax({
                type: "POST",
                url: self.options.api_unfollow,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", getMetaCSRFToken());
                },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    self.element.find(".dj-answers-follow").removeClass(
                        "dj-off").addClass("dj-on");
                    self.element.find(".dj-answers-unfollow").removeClass(
                        "dj-on").addClass("dj-off");
                    showMessages(
                        ['You will no longer receive e-mails for additional'
                        + ' comments on "' + data.title + '".'], "success");
                },
                error: function(resp) {
                    showErrorMessages(resp, "error");
                },
            });
        },

        upvote: function () {
            var self = this;
            $.ajax({
                type: "POST",
                url: self.options.api_upvote,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", getMetaCSRFToken());
                },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    self.element.find(".dj-answers-uservote").removeClass(
                        "dj-off").addClass("dj-on");
                    self.element.find(".dj-answers-upvote").removeClass(
                        "dj-on").addClass("dj-off");
                    self.element.find(".dj-answers-downvote").removeClass(
                        "dj-on").addClass("dj-off");
                },
                error: function(resp) {
                    showErrorMessages(resp, "error");
                },
            });
        },

        downvote: function () {
            var self = this;
            $.ajax({
                type: "POST",
                url: self.options.api_downvote,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", getMetaCSRFToken());
                },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    self.element.find(".dj-answers-uservote").removeClass(
                        "dj-off").addClass("dj-on");
                    self.element.find(".dj-answers-upvote").removeClass(
                        "dj-on").addClass("dj-off");
                    self.element.find(".dj-answers-downvote").removeClass(
                        "dj-on").addClass("dj-off");
                    showMessages(
                        ['You will now receive an e-mail for new comments on "'
                        + data.title + '".'], "success");
                },
                error: function(resp) {
                    showErrorMessages(resp, "error");
                },
            });
        },
    };

    $.fn.djForumQuestion = function(options) {
        var opts = $.extend( {}, $.fn.djForumQuestion.defaults, options );
        return new ForumQuestion($(this), opts);
    };

    $.fn.djForumQuestion.defaults = {
        api_follow: null,
        api_unfollow: null,
        api_upvote: null,
        api_downvote: null
    };

})(jQuery);
