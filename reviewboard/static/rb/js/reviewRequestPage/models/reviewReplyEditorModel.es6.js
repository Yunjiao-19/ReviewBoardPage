/**
 * An editor for replying to parts of a review.
 *
 * This will track the editing state of a reply to the body top/bottom of
 * a review or a comment, and handles saving of the reply.
 */
RB.ReviewRequestPage.ReviewReplyEditor = Backbone.Model.extend({
    defaults: {
        anchorPrefix: null,
        contextID: null,
        contextType: null,
        commentID: null,
        hasDraft: false,
        replyObject: null,
        review: null,
        reviewReply: null,
        richText: null,
        text: '',
    },

    replyClasses: {
        diff_comments: RB.DiffCommentReply,
        screenshot_comments: RB.ScreenshotCommentReply,
        file_attachment_comments: RB.FileAttachmentCommentReply,
        general_comments: RB.GeneralCommentReply,
        untouched_comments: RB.UntouchedCommentReply,
    },

    /**
     * Initialize the model.
     */
    initialize() {
        this.on('change:reviewReply', this._setupReviewReply, this);
        this._setupReviewReply();
    },

    /**
     * Save the current reply.
     *
     * This will trigger the "saving" event before saving, and will trigger
     * "saved" after it succeeds.
     */
    save() {
        const contextType = this.get('contextType');
        const reviewReply = this.get('reviewReply');
        let valueAttr;
        let richTextAttr;
        let obj;

        if (contextType === 'body_top') {
            valueAttr = 'bodyTop';
            richTextAttr = 'bodyTopRichText';
            obj = reviewReply;
        } else if (contextType === 'body_bottom') {
            valueAttr = 'bodyBottom';
            richTextAttr = 'bodyBottomRichText';
            obj = reviewReply;
        } else {
            valueAttr = 'text';
            richTextAttr = 'richText';
            obj = this.get('replyObject');

            if (!obj) {
                const ReplyClass = this.replyClasses[contextType];

                console.assert(ReplyClass,
                               "Unexpected context type '%s'",
                               contextType);

                obj = new ReplyClass({
                    parentObject: reviewReply,
                    replyToID: this.get('contextID'),
                    id: this.get('commentID'),
                });
            }
        }

        this.set('replyObject', obj);

        this.trigger('saving');

        obj.ready({
            ready: () => {
                const text = this.get('text');

                if (text) {
                    obj.set(valueAttr, text);
                    obj.set(richTextAttr, this.get('richText'));
                    obj.set({
                        forceTextType: 'html',
                        includeTextTypes: 'raw',
                    });

                    obj.save({
                        attrs: [valueAttr, richTextAttr, 'forceTextType',
                                'includeTextTypes', 'replyToID'],
                        success: function() {
                            this.set({
                                hasDraft: true,
                                text: obj.get(valueAttr),
                                richText: true,
                            });
                            this.trigger('textUpdated');
                            this.trigger('saved');
                        }
                    }, this);
                } else {
                    this.resetStateIfEmpty();
                }
            },
        });
    },

    /**
     * Reset the editor state, if the text isn't set.
     *
     * If the text attribute has a value, this will do nothing.
     * Otherwise, it will destroy the reply or the comment (depending on
     * what is being replied to), and then trigger "resetState".
     */
    resetStateIfEmpty() {
        const text = this.get('text');

        if (text.strip() !== '') {
            return;
        }

        const replyObject = this.get('replyObject');

        if (!replyObject || replyObject.isNew()) {
            this._resetState();
        } else {
            const contextType = this.get('contextType');

            if (contextType === 'body_top' ||
                contextType === 'body_bottom') {
                this._resetState(true);
            } else {
                replyObject.destroy({
                    success: this._resetState
                }, this);
            }
        }
    },

    /**
     * Set up a new ReviewReply for this editor.
     *
     * This will first stop listening to any events on an old reviewReply.
     *
     * It will then listen for "destroy" and "published" events on the new
     * reply. If either triggers, the "discarded" or "published" signals
     * (respectively) will be triggered, and the state of the editor will reset.
     */
    _setupReviewReply() {
        const reviewReply = this.get('reviewReply');
        const oldReviewReply = this.previous('reviewReply');

        if (oldReviewReply) {
            oldReviewReply.off(null, null, this);
        }

        this.listenTo(reviewReply, 'destroyed', () => {
            this.trigger('discarded');
            this._resetState();
        });

        this.listenTo(reviewReply, 'published', () => {
            this.trigger('published');
            this._resetState(false);
        });
    },

    /**
     * Resets the state of the editor.
     *
     * Args:
     *     shouldDiscardIfEmpty (boolean):
     *         Whether to discard the entire reply if there are no individual
     *         comments.
     */
    _resetState: function(shouldDiscardIfEmpty) {
        this.set({
            commentID: null,
            hasDraft: false,
            replyObject: null,
        });

        if (shouldDiscardIfEmpty === false) {
            this.trigger('resetState');
        } else {
            this.get('reviewReply').discardIfEmpty({
                success: () => this.trigger('resetState'),
            });
        }
    },
});
