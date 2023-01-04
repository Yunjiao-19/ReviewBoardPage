suite('rb/resources/models/CommitMessageComment', function() {
    let model;

    beforeEach(function() {
        /* Set some sane defaults needed to pass validation. */
        model = new RB.CommitMessageComment({
            diffCommitID: 16,
            parentObject: new RB.BaseResource({
                'public': true,
            })
        });
    });

    describe('parse', function() {
        it('API payloads', function() {
            const data = model.parse({
                stat: 'ok',
                commit_comment: {
                    id: 42,
                    issue_opened: true,
                    issue_status: 'resolved',
                    text_type: 'markdown',
                    text: 'foo',
                    first_line: 10,
                    num_lines: 5,
                    diff_commit: {
                        author_name: 'Author Name',
                        commit_id: 'r123',
                        commit_message: 'A commit message.',
                        id: 1,
                        parent_id: 'r122'
                    }
                },
            });

            expect(data).not.toBe(undefined);
            expect(data.id).toBe(42);
            expect(data.issueOpened).toBe(true);
            expect(data.issueStatus).toBe(RB.BaseComment.STATE_RESOLVED);
            expect(data.richText).toBe(true);
            expect(data.text).toBe('foo');
            expect(data.diffCommit).not.toBe(undefined);
            expect(data.diffCommit.id).toBe(1);
            expect(data.diffCommit.get('commitMessage')).toBe('A commit message.');
            expect(data.diffCommit.get('authorName')).toBe('Author Name');
            expect(data.diffCommit.get('commitID')).toBe('r123');
            expect(data.diffCommit.get('parentID')).toBe('r122');
        });
    });

    describe('toJSON', function() {
        it('BaseComment.toJSON called', function() {
            spyOn(RB.BaseComment.prototype, 'toJSON').and.callThrough();
            model.toJSON();
            expect(RB.BaseComment.prototype.toJSON).toHaveBeenCalled();
        });

        describe('force_text_type field', function() {
            it('With value', function() {
                model.set('forceTextType', 'html');
                const data = model.toJSON();
                expect(data.force_text_type).toBe('html');
            });

            it('Without value', function() {
                const data = model.toJSON();
                expect(data.force_text_type).toBe(undefined);
            });
        });

        describe('include_text_types field', function() {
            it('With value', function() {
                model.set('includeTextTypes', 'html');
                const data = model.toJSON();
                expect(data.include_text_types).toBe('html');
            });

            it('Without value', function() {
                const data = model.toJSON();

                expect(data.include_text_types).toBe(undefined);
            });
        });

        describe('commit_id field', function() {
            it('When loaded', function() {
                model.set('loaded', true);
                const data = model.toJSON();
                expect(data.commit_id).toBe(undefined);
            });

            it('When not loaded', function() {
                const data = model.toJSON();
                expect(data.commit_id).toBe(16);
            });
        });
    });

    describe('validate', function() {
        it('Inherited behavior', function() {
            spyOn(RB.BaseComment.prototype, 'validate');
            model.validate({});
            expect(RB.BaseComment.prototype.validate).toHaveBeenCalled();
        });


        describe('diffCommitID', function() {
            it('With value', function() {
                expect(model.validate({
                    diffCommitID: 42,
                })).toBe(undefined);
            });

            it('Unset', function() {
                expect(model.validate({
                    diffCommitID: null,
                })).toBe(RB.CommitMessageComment.strings.INVALID_DIFFCOMMIT_ID);
            });
        });
    });
});
