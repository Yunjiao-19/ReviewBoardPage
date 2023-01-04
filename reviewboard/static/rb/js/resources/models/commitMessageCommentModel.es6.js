/**
 * Provides commenting functionality for commits.
 *
 * A CommitMessageComment represents a comment on a DiffCommit.
 *
 * Model Attributes:
 *      diffCommit (RB.DiffCommit):
 *         The DiffCommit that the comment applies to.
 *
 *      diffCommitID (number):
 *         The ID of the DiffCommit that the comment applies to.
 */
 RB.CommitMessageComment = RB.BaseComment.extend({
    defaults: _.defaults({
        diffCommit: null,
        diffCommitID: null,
    }, RB.BaseComment.prototype.defaults()),

    rspNamespace: 'commit_message_comment',
    expandedFields: ['diff_commit'],

    attrToJsonMap: _.defaults({
        diffCommitID: 'commit_id'
    }, RB.BaseComment.prototype.attrToJsonMap),

    serializedAttrs: [
        'diffCommitID',
    ].concat(RB.BaseComment.prototype.serializedAttrs),

    serializers: _.defaults({
        diffCommitID: RB.JSONSerializers.onlyIfUnloaded,
    }, RB.BaseComment.prototype.serializers),
    
    /**
     * Deserialize comment data from an API payload.
     *
     * Args:
     *     rsp (object):
     *         The data from the server.
     *
     * Returns:
     *     object:
     *     The model attributes to assign.
     */
    parseResourceData(rsp) {
        const result = RB.BaseComment.prototype.parseResourceData.call(
            this, rsp);

        return result;
    },

    /**
     * Perform validation on the attributes of the model.
     *
     * This will check the commit message id.
     *
     * Args:
     *     attrs (object):
     *         The set of attributes to validate.
     *
     * Returns:
     *     string:
     *     An error string, if appropriate.
     */
    validate(attrs) {
        if (this.isNew() && _.has(attrs, 'diffCommitID') && !attrs.diffCommitID) {
            return RB.CommitMessageComment.strings.INVALID_DIFFCOMMIT_ID;
        }
        
        return RB.BaseComment.prototype.validate.apply(this, arguments);
    }
}, {
    strings: {
        INVALID_DIFFCOMMIT_ID: 'diffCommitID must be a valid ID',
    }
});
