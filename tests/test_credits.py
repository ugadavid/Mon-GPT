"""MG-012 : notices intègres et fenêtre documentaire hors ligne, sans écriture."""
import hashlib
import json
from pathlib import Path
import platform
import tkinter as tk
import unittest
from unittest.mock import patch
import PIL
import test_batch_ui as helpers
from mon_gpt.credits import COMPONENTS,NOTICES,SCOPE,read_notice
from mon_gpt.storage import encode


class CreditsTests(unittest.TestCase):
    setUp=helpers.BatchUITests.setUp
    destroy=helpers.BatchUITests.destroy

    def test_reference_integrity_attributions_and_actual_versions(self):
        manifest=json.loads((NOTICES/'sources.json').read_text(encoding='utf-8'))
        self.assertEqual({r['file'] for r in manifest['notices']},{c.file for c in COMPONENTS})
        for entry in manifest['notices']:
            text=(NOTICES/entry['file']).read_text(encoding='utf-8')
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),entry['sha256_lf_utf8'])
        python,tcl,tk,pillow=[read_notice(c) for c in COMPONENTS]
        for attribution in ('PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2','BEOPEN','CNRI','CWI','ZERO-CLAUSE BSD','Additional Conditions for this Windows binary build'):
            self.assertIn(attribution,python)
        self.assertIn('252.227-7014',tcl);self.assertIn('252.227-7013',tk)
        for attribution in ('MIT-CMU','Secret Labs AB','Fredrik Lundh',"Jeffrey 'Alex' Clark",'===== zlib-ng-'):
            self.assertIn(attribution,pillow)
        self.assertEqual(Path('requirements.txt').read_text().strip(),'Pillow==13.0.0')
        w=self.app.credits();self.root.update()
        self.assertEqual(w.versions,(platform.python_version(),str(self.root.tk.call('info','patchlevel')),str(self.root.tk.call('package','present','Tk')),PIL.__version__))
        self.assertEqual([c.name for c in COMPONENTS],['Python','Tcl','Tk','Pillow'])
        self.assertIn('licence générale de son code n’est pas encore fixée',SCOPE)
        self.assertIn('Puppeteer est réservé à ses tests',SCOPE)
        w.close()

    def test_menu_lifecycle_offline_single_window_focus_and_no_writes(self):
        self.app.save_preferences();prefs=self.store.directory/'interface.json'
        before=(encode(self.app.cat,self.app.adapter),self.store.path.read_bytes(),prefs.read_bytes())
        self.table.focus_force();self.root.update()
        menu=dict(self.app.main_menu.menus)['Aide']
        labels=[menu.entrycget(i,'label') for i in range(menu.index('end')+1)]
        self.assertEqual(labels,['Gestes et raccourcis','Licences et crédits…','À propos de Mon GPT<3'])
        with patch('socket.create_connection',side_effect=AssertionError('Réseau interdit')),patch('mon_gpt.credits_ui.webbrowser.open') as network,patch.object(self.store,'save') as save,patch('mon_gpt.ui_state.save') as preferences:
            menu.invoke(1);self.root.update();w=self.app.credits_window
            self.assertEqual(w,self.app.credits())
            self.assertEqual(len([c for c in self.root.winfo_children() if isinstance(c,tk.Toplevel) and c.title().startswith('Licences et crédits')]),1)
            for n in range(4):
                w.table.selection_set(str(n));w.table.event_generate('<<TreeviewSelect>>');w.consult();self.root.update()
                self.assertEqual(w.notice_choice.current(),n)
                self.assertEqual(w.notice_text.get('1.0','end-1c'),read_notice(COMPONENTS[n]))
            w.notice_choice.focus_force();self.root.update();w.notice_choice.event_generate('<Escape>');self.root.update()
            self.assertFalse(w.winfo_exists());self.assertEqual(self.root.focus_get(),self.table)
            second=self.app.credits();self.root.update();self.assertNotEqual(w,second)
            second.close_button.invoke();self.root.update()
            network.assert_not_called();save.assert_not_called();preferences.assert_not_called()
        self.assertEqual(before,(encode(self.app.cat,self.app.adapter),self.store.path.read_bytes(),prefs.read_bytes()))

    def test_notice_selection_copy_scroll_resize_keyboard_and_optional_source(self):
        w=self.app.credits();self.root.update()
        for width,height in ((860,640),(600,500),(1100,760)):
            w.geometry(f'{width}x{height}');self.root.update()
            self.assertTrue(w.close_button.winfo_viewable())
            self.assertGreater(w.detail.winfo_height(),20)
            self.assertLessEqual(w.close_button.winfo_rooty()+w.close_button.winfo_height(),w.winfo_rooty()+height)
            w.table.selection_set('3');w.table.focus('3');w.table.focus_force();self.root.update()
            w.table.event_generate('<Return>');self.root.update()
            self.assertEqual(w.tabs.index('current'),1)
            self.assertEqual(w.notice_text.cget('state'),'disabled')
            w.notice_text.yview_moveto(1);self.root.update()
            self.assertGreater(w.notice_text.yview()[0],0)
            self.assertIn('This notice may not be removed',w.notice_text.get('@0,0','end'))
            w.notice_choice.current(1);w.notice_choice.event_generate('<<ComboboxSelected>>');self.root.update()
            self.assertEqual(w.notice_text.get('1.0','end-1c'),read_notice(COMPONENTS[1]))
            w.notice_text.focus_force();self.root.update()
            w.notice_text.event_generate('<Control-a>');w.notice_text.event_generate('<<Copy>>');self.root.update()
            self.assertEqual(self.root.clipboard_get(),read_notice(COMPONENTS[1]))
            w.notice_text.event_generate('<Tab>');self.root.update();self.assertNotEqual(self.root.focus_get(),w.notice_text)
            w.tabs.select(0)
        with patch('mon_gpt.credits_ui.webbrowser.open') as browser:
            w.table.selection_set('3');w.source_button.invoke()
            browser.assert_called_once_with(COMPONENTS[3].url,new=2)
        w.close();self.root.clipboard_clear()

    def test_missing_notice_is_readable_without_network_fallback(self):
        w=self.app.credits();self.root.update()
        with patch('mon_gpt.credits_ui.read_notice',side_effect=FileNotFoundError),patch('mon_gpt.credits_ui.webbrowser.open') as network:
            w.consult();self.assertIn('Notice locale indisponible',w.notice_text.get('1.0','end'))
            network.assert_not_called()
        w.close()
